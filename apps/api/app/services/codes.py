from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SubmissionCounter


def next_public_code(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    counter = db.execute(
        select(SubmissionCounter).where(SubmissionCounter.year == year).with_for_update()
    ).scalar_one_or_none()
    if counter is None:
        counter = SubmissionCounter(year=year, last_value=0)
        db.add(counter)
        db.flush()
    counter.last_value += 1
    db.flush()
    return f"SUB-{year}-{counter.last_value:06d}"
