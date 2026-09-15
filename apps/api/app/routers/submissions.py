from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.db import Asset, AssetStatus, Submission, SubmissionStatus
from app.schemas import SubmissionCreate, SubmissionCreated, SubmissionOut, AssetOut
from app.services.audit import audit
from app.services.codes import next_public_code
from app.services.images import sha256_bytes, validate_image_bytes
from app.services.queue import enqueue_process_submission
from app.session import get_db
from app.storage import put_bytes

router = APIRouter(tags=["submissions"])


def _submission_out(sub: Submission, *, mark_dupes: bool = False) -> SubmissionOut:
    assets = []
    seen_sha: set[str] = set()
    for a in sub.assets:
        dup = False
        if mark_dupes and a.sha256 in seen_sha:
            dup = True
        seen_sha.add(a.sha256)
        assets.append(
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
                duplicate_of_existing_file=dup,
            )
        )
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
        assets=assets,
    )


@router.post("/submissions", response_model=SubmissionCreated, status_code=201)
def create_submission(body: SubmissionCreate, db: Session = Depends(get_db)) -> SubmissionCreated:
    if not body.terms_accepted:
        raise HTTPException(400, "É necessário aceitar os termos.")

    code = next_public_code(db)
    sub = Submission(
        public_code=code,
        sender_name=body.sender_name,
        sender_email=str(body.sender_email),
        relation=body.relationship,
        photo_date_text=body.photo_date_text,
        date_precision=body.date_precision,
        location=body.location,
        people=body.people,
        story=body.story,
        author_name=body.author_name,
        publication_authorized=body.publication_authorized,
        terms_accepted=body.terms_accepted,
        status=SubmissionStatus.RECEIVED,
    )
    db.add(sub)
    db.flush()
    audit(
        db,
        entity_type="submission",
        entity_id=sub.id,
        action="created",
        details={"public_code": code},
    )
    db.commit()
    db.refresh(sub)
    return SubmissionCreated(
        id=sub.id,
        public_code=sub.public_code,
        status=sub.status,
        message=(
            "Submissão registrada. Envie as imagens e finalize o envio. "
            "Nada será publicado sem revisão."
        ),
    )


@router.post("/submissions/{submission_id}/files", response_model=AssetOut, status_code=201)
async def upload_file(
    submission_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> AssetOut:
    settings = get_settings()
    sub = db.get(Submission, submission_id)
    if sub is None:
        raise HTTPException(404, "Submissão não encontrada.")
    if sub.status not in {SubmissionStatus.RECEIVED, SubmissionStatus.CHANGES_REQUESTED}:
        raise HTTPException(400, "Esta submissão não aceita novos arquivos no estado atual.")

    count = len(sub.assets)
    if count >= settings.max_files_per_submission:
        raise HTTPException(400, f"Limite de {settings.max_files_per_submission} arquivos por submissão.")

    data = await file.read()
    try:
        mime, ext = validate_image_bytes(data, settings.max_upload_bytes)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    digest = sha256_bytes(data)

    # Exact dedup: reuse existing object_key if same hash already stored
    existing = db.execute(select(Asset).where(Asset.sha256 == digest).limit(1)).scalar_one_or_none()
    reused = False
    if existing is not None:
        object_key = existing.object_key
        reused = True
    else:
        object_key = f"{digest[:2]}/{digest}/{uuid.uuid4().hex}{ext}"
        put_bytes(settings.bucket_quarantine, object_key, data, mime)

    asset = Asset(
        submission_id=sub.id,
        original_filename=(file.filename or f"upload{ext}")[:500],
        object_key=object_key,
        sha256=digest,
        mime_type=mime,
        size_bytes=len(data),
        status=AssetStatus.UPLOADED,
    )
    db.add(asset)
    db.flush()
    audit(
        db,
        entity_type="asset",
        entity_id=asset.id,
        action="uploaded",
        details={"sha256": digest, "reused_object": reused, "size": len(data)},
    )
    db.commit()
    db.refresh(asset)
    return AssetOut(
        id=asset.id,
        original_filename=asset.original_filename,
        mime_type=asset.mime_type,
        size_bytes=asset.size_bytes,
        width=asset.width,
        height=asset.height,
        sha256=asset.sha256,
        status=asset.status,
        has_thumbnail=False,
        duplicate_of_existing_file=reused,
    )


@router.post("/submissions/{submission_id}/complete", response_model=SubmissionOut)
def complete_submission(submission_id: uuid.UUID, db: Session = Depends(get_db)) -> SubmissionOut:
    sub = db.execute(
        select(Submission)
        .where(Submission.id == submission_id)
        .options(selectinload(Submission.assets))
    ).scalar_one_or_none()
    if sub is None:
        raise HTTPException(404, "Submissão não encontrada.")
    if not sub.assets:
        raise HTTPException(400, "Envie ao menos uma imagem antes de finalizar.")
    if sub.status not in {SubmissionStatus.RECEIVED, SubmissionStatus.CHANGES_REQUESTED}:
        raise HTTPException(400, "Submissão já foi finalizada.")

    sub.status = SubmissionStatus.QUEUED
    audit(db, entity_type="submission", entity_id=sub.id, action="queued")
    db.commit()

    try:
        enqueue_process_submission(str(sub.id))
    except Exception as exc:  # noqa: BLE001
        sub.status = SubmissionStatus.ERROR
        audit(
            db,
            entity_type="submission",
            entity_id=sub.id,
            action="queue_error",
            details={"error": str(exc)},
        )
        db.commit()
        raise HTTPException(500, "Não foi possível enfileirar o processamento.") from exc

    db.refresh(sub)
    return _submission_out(sub)
