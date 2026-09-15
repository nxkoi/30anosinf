from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.db import Asset, Milestone, Submission, SubmissionStatus
from app.schemas import MilestoneOut, PublicAssetOut
from app.session import get_db
from app.storage import get_bytes

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/timeline", response_model=list[MilestoneOut])
def timeline(db: Session = Depends(get_db)) -> list[MilestoneOut]:
    rows = db.execute(select(Milestone).order_by(Milestone.sort_order, Milestone.year)).scalars().all()
    return [MilestoneOut.model_validate(r) for r in rows]


@router.get("/assets", response_model=list[PublicAssetOut])
def list_published(db: Session = Depends(get_db)) -> list[PublicAssetOut]:
    subs = db.execute(
        select(Submission)
        .where(Submission.status == SubmissionStatus.PUBLISHED)
        .options(selectinload(Submission.assets))
        .order_by(Submission.updated_at.desc())
    ).scalars().all()
    out: list[PublicAssetOut] = []
    for sub in subs:
        for asset in sub.assets:
            if asset.approved_key:
                out.append(
                    PublicAssetOut(
                        id=asset.id,
                        public_code=sub.public_code,
                        photo_date_text=sub.photo_date_text,
                        date_precision=sub.date_precision,
                        location=sub.location,
                        people=sub.people,
                        story=sub.story,
                        author_name=sub.author_name,
                        relationship=sub.relation,
                        width=asset.width,
                        height=asset.height,
                        media_url=f"/api/public/assets/{asset.id}/media",
                        published_at=sub.updated_at,
                    )
                )
    return out


@router.get("/assets/{asset_id}", response_model=PublicAssetOut)
def get_published(asset_id: uuid.UUID, db: Session = Depends(get_db)) -> PublicAssetOut:
    asset = db.execute(
        select(Asset)
        .where(Asset.id == asset_id)
        .options(selectinload(Asset.submission))
    ).scalar_one_or_none()
    if asset is None or asset.submission.status != SubmissionStatus.PUBLISHED or not asset.approved_key:
        raise HTTPException(404, "Item não encontrado.")
    sub = asset.submission
    return PublicAssetOut(
        id=asset.id,
        public_code=sub.public_code,
        photo_date_text=sub.photo_date_text,
        date_precision=sub.date_precision,
        location=sub.location,
        people=sub.people,
        story=sub.story,
        author_name=sub.author_name,
        relationship=sub.relation,
        width=asset.width,
        height=asset.height,
        media_url=f"/api/public/assets/{asset.id}/media",
        published_at=sub.updated_at,
    )


@router.get("/assets/{asset_id}/media")
def media(asset_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    settings = get_settings()
    asset = db.execute(
        select(Asset)
        .where(Asset.id == asset_id)
        .options(selectinload(Asset.submission))
    ).scalar_one_or_none()
    if asset is None or asset.submission.status != SubmissionStatus.PUBLISHED or not asset.approved_key:
        raise HTTPException(404, "Mídia não disponível.")
    data = get_bytes(settings.bucket_approved, asset.approved_key)
    return Response(content=data, media_type="image/webp", headers={"Cache-Control": "public, max-age=300"})
