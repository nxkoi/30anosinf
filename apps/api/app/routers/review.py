from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import require_review_auth
from app.config import get_settings
from app.db import (
    Analysis,
    Asset,
    AssetStatus,
    Review,
    ReviewStatus,
    Submission,
    SubmissionStatus,
)
from app.schemas import AnalysisOut, AssetOut, NotesBody, ReviewOut, SubmissionOut
from app.services.audit import audit
from app.session import get_db
from app.storage import copy_object, get_bytes

router = APIRouter(prefix="/review", tags=["review"], dependencies=[Depends(require_review_auth)])


def _serialize(sub: Submission) -> SubmissionOut:
    analyses: list[AnalysisOut] = []
    assets_out: list[AssetOut] = []
    for a in sub.assets:
        assets_out.append(
            AssetOut(
                id=a.id,
                original_filename=a.original_filename,
                mime_type=a.mime_type,
                size_bytes=a.size_bytes,
                width=a.width,
                height=a.height,
                sha256=a.sha256,
                status=a.status,
                has_thumbnail=bool(a.derived_key),
            )
        )
        for an in a.analyses:
            analyses.append(AnalysisOut.model_validate(an))
    reviews = [ReviewOut.model_validate(r) for r in sub.reviews]
    return SubmissionOut(
        id=sub.id,
        public_code=sub.public_code,
        sender_name=sub.sender_name,
        sender_email=sub.sender_email,
        relationship=sub.relation,
        photo_date_text=sub.photo_date_text,
        date_precision=sub.date_precision,
        location=sub.location,
        people=sub.people,
        story=sub.story,
        author_name=sub.author_name,
        publication_authorized=sub.publication_authorized,
        terms_accepted=sub.terms_accepted,
        status=sub.status,
        created_at=sub.created_at,
        updated_at=sub.updated_at,
        assets=assets_out,
        analyses=analyses,
        reviews=reviews,
    )


def _load(db: Session, submission_id: uuid.UUID) -> Submission:
    sub = db.execute(
        select(Submission)
        .where(Submission.id == submission_id)
        .options(
            selectinload(Submission.assets).selectinload(Asset.analyses),
            selectinload(Submission.reviews),
        )
    ).scalar_one_or_none()
    if sub is None:
        raise HTTPException(404, "Submissão não encontrada.")
    return sub


@router.get("/submissions", response_model=list[SubmissionOut])
def list_submissions(
    status_filter: SubmissionStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[SubmissionOut]:
    stmt = (
        select(Submission)
        .options(
            selectinload(Submission.assets).selectinload(Asset.analyses),
            selectinload(Submission.reviews),
        )
        .order_by(Submission.created_at.desc())
    )
    if status_filter is not None:
        stmt = stmt.where(Submission.status == status_filter)
    rows = db.execute(stmt).scalars().all()
    return [_serialize(s) for s in rows]


@router.get("/submissions/{submission_id}", response_model=SubmissionOut)
def get_submission(submission_id: uuid.UUID, db: Session = Depends(get_db)) -> SubmissionOut:
    return _serialize(_load(db, submission_id))


@router.get("/assets/{asset_id}/thumbnail")
def get_thumbnail(asset_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    settings = get_settings()
    asset = db.get(Asset, asset_id)
    if asset is None or not asset.derived_key:
        raise HTTPException(404, "Miniatura não disponível.")
    data = get_bytes(settings.bucket_derived, asset.derived_key)
    return Response(content=data, media_type="image/webp", headers={"Cache-Control": "private, max-age=60"})


@router.post("/submissions/{submission_id}/approve", response_model=SubmissionOut)
def approve(
    submission_id: uuid.UUID,
    body: NotesBody | None = None,
    db: Session = Depends(get_db),
) -> SubmissionOut:
    sub = _load(db, submission_id)
    if sub.status not in {
        SubmissionStatus.READY_FOR_REVIEW,
        SubmissionStatus.CHANGES_REQUESTED,
        SubmissionStatus.APPROVED,
    }:
        raise HTTPException(400, f"Não é possível aprovar no estado {sub.status.value}.")

    notes = body.notes if body else None
    sub.status = SubmissionStatus.APPROVED
    for a in sub.assets:
        if a.status == AssetStatus.READY:
            a.status = AssetStatus.APPROVED
    review = Review(
        submission_id=sub.id,
        status=ReviewStatus.APPROVED,
        review_notes=notes,
        approved_at=datetime.now(timezone.utc),
    )
    db.add(review)
    audit(
        db,
        entity_type="submission",
        entity_id=sub.id,
        action="approved",
        details={"notes": notes},
    )
    db.commit()
    return _serialize(_load(db, submission_id))


@router.post("/submissions/{submission_id}/request-changes", response_model=SubmissionOut)
def request_changes(
    submission_id: uuid.UUID,
    body: NotesBody,
    db: Session = Depends(get_db),
) -> SubmissionOut:
    sub = _load(db, submission_id)
    if sub.status in {SubmissionStatus.PUBLISHED, SubmissionStatus.REJECTED}:
        raise HTTPException(400, "Estado final; não é possível solicitar ajustes.")
    sub.status = SubmissionStatus.CHANGES_REQUESTED
    db.add(
        Review(
            submission_id=sub.id,
            status=ReviewStatus.CHANGES_REQUESTED,
            review_notes=body.notes,
        )
    )
    audit(
        db,
        entity_type="submission",
        entity_id=sub.id,
        action="changes_requested",
        details={"notes": body.notes},
    )
    db.commit()
    return _serialize(_load(db, submission_id))


@router.post("/submissions/{submission_id}/reject", response_model=SubmissionOut)
def reject(
    submission_id: uuid.UUID,
    body: NotesBody,
    db: Session = Depends(get_db),
) -> SubmissionOut:
    sub = _load(db, submission_id)
    if sub.status == SubmissionStatus.PUBLISHED:
        raise HTTPException(400, "Item publicado não pode ser rejeitado por este fluxo.")
    sub.status = SubmissionStatus.REJECTED
    for a in sub.assets:
        a.status = AssetStatus.REJECTED
    db.add(
        Review(
            submission_id=sub.id,
            status=ReviewStatus.REJECTED,
            review_notes=body.notes,
        )
    )
    audit(
        db,
        entity_type="submission",
        entity_id=sub.id,
        action="rejected",
        details={"notes": body.notes},
    )
    db.commit()
    return _serialize(_load(db, submission_id))


@router.post("/submissions/{submission_id}/publish", response_model=SubmissionOut)
def publish(
    submission_id: uuid.UUID,
    body: NotesBody | None = None,
    db: Session = Depends(get_db),
) -> SubmissionOut:
    settings = get_settings()
    sub = _load(db, submission_id)

    if not sub.publication_authorized:
        raise HTTPException(
            400,
            "Publicação bloqueada: o autor não autorizou a publicação desta contribuição.",
        )
    if sub.status != SubmissionStatus.APPROVED:
        raise HTTPException(400, "Só é possível publicar itens previamente aprovados.")

    for asset in sub.assets:
        if not asset.derived_key:
            raise HTTPException(400, f"Asset {asset.id} sem derivado.")
        approved_key = f"{asset.sha256[:2]}/{asset.sha256}/{asset.id}.webp"
        copy_object(settings.bucket_derived, asset.derived_key, settings.bucket_approved, approved_key)
        asset.approved_key = approved_key
        asset.status = AssetStatus.PUBLISHED

    notes = body.notes if body else None
    sub.status = SubmissionStatus.PUBLISHED
    db.add(
        Review(
            submission_id=sub.id,
            status=ReviewStatus.PUBLISHED,
            review_notes=notes,
            approved_at=datetime.now(timezone.utc),
        )
    )
    audit(
        db,
        entity_type="submission",
        entity_id=sub.id,
        action="published",
        details={"notes": notes},
    )
    db.commit()
    return _serialize(_load(db, submission_id))
