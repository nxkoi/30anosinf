from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.db import AuditEvent


def audit(
    db: Session,
    *,
    entity_type: str,
    entity_id: str | uuid.UUID,
    action: str,
    details: dict[str, Any] | None = None,
) -> None:
    db.add(
        AuditEvent(
            entity_type=entity_type,
            entity_id=str(entity_id),
            action=action,
            details=details or {},
        )
    )
