from __future__ import annotations

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.db import Analysis, Asset, AssetStatus, Review, ReviewStatus, Submission, SubmissionStatus
from app.providers import get_image_provider
from app.services.audit import audit
from app.services.images import image_dimensions, make_thumbnail_webp
from app.session import SessionLocal
from app.storage import copy_object, get_bytes, put_bytes

logger = logging.getLogger(__name__)


def process_submission(submission_id: str) -> None:
    """RQ job: process uploaded assets with mock analysis."""
    db = SessionLocal()
    settings = get_settings()
    try:
        submission = db.execute(
            select(Submission)
            .where(Submission.id == uuid.UUID(submission_id))
            .options(selectinload(Submission.assets))
        ).scalar_one_or_none()
        if submission is None:
            logger.error("submission not found: %s", submission_id)
            return

        submission.status = SubmissionStatus.PROCESSING
        audit(db, entity_type="submission", entity_id=submission.id, action="processing_started")
        db.commit()

        provider = get_image_provider()

        for asset in submission.assets:
            try:
                asset.status = AssetStatus.PROCESSING
                db.commit()

                data = get_bytes(settings.bucket_quarantine, asset.object_key)
                width, height = image_dimensions(data)
                asset.width = width
                asset.height = height

                # Promote to originals if not already there (deduped uploads reuse key)
                originals_key = asset.object_key
                try:
                    copy_object(
                        settings.bucket_quarantine,
                        asset.object_key,
                        settings.bucket_originals,
                        originals_key,
                    )
                except Exception:
                    # Object may already exist in originals from a previous identical upload
                    pass

                thumb = make_thumbnail_webp(data)
                derived_key = f"{asset.sha256[:2]}/{asset.sha256}/{asset.id}.webp"
                put_bytes(settings.bucket_derived, derived_key, thumb, "image/webp")
                asset.derived_key = derived_key

                result = provider.analyze(
                    data,
                    {
                        "submission_id": str(submission.id),
                        "asset_id": str(asset.id),
                        "public_code": submission.public_code,
                        "original_filename": asset.original_filename,
                    },
                )
                db.add(
                    Analysis(
                        asset_id=asset.id,
                        provider=result["provider"],
                        model=result["model"],
                        description=result["description"],
                        structured_result=result.get("structured_result") or {},
                        status=result.get("status", "DONE"),
                    )
                )
                asset.status = AssetStatus.READY
                db.commit()
            except Exception as exc:  # noqa: BLE001
                logger.exception("asset processing failed: %s", asset.id)
                asset.status = AssetStatus.ERROR
                submission.status = SubmissionStatus.ERROR
                audit(
                    db,
                    entity_type="asset",
                    entity_id=asset.id,
                    action="processing_error",
                    details={"error": str(exc)},
                )
                db.commit()
                return

        submission.status = SubmissionStatus.READY_FOR_REVIEW
        db.add(Review(submission_id=submission.id, status=ReviewStatus.PENDING))
        audit(
            db,
            entity_type="submission",
            entity_id=submission.id,
            action="ready_for_review",
        )
        db.commit()
    finally:
        db.close()
