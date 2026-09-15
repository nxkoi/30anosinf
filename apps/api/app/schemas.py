from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.db import AssetStatus, ReviewStatus, SubmissionStatus


def sanitize_text(value: str | None, max_len: int = 5000) -> str | None:
    if value is None:
        return None
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", value).strip()
    if not cleaned:
        return None
    return cleaned[:max_len]


class SubmissionCreate(BaseModel):
    sender_name: str = Field(min_length=2, max_length=200)
    sender_email: EmailStr
    relationship: str = Field(min_length=2, max_length=200)
    photo_date_text: str | None = Field(default=None, max_length=200)
    date_precision: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=300)
    people: str | None = None
    story: str | None = None
    author_name: str | None = Field(default=None, max_length=200)
    publication_authorized: bool
    terms_accepted: bool

    @field_validator(
        "sender_name",
        "relationship",
        "photo_date_text",
        "date_precision",
        "location",
        "people",
        "story",
        "author_name",
        mode="before",
    )
    @classmethod
    def _sanitize(cls, v: Any) -> Any:
        if isinstance(v, str):
            return sanitize_text(v, 8000)
        return v

    @field_validator("terms_accepted")
    @classmethod
    def terms_must_be_true(cls, v: bool) -> bool:
        if not v:
            raise ValueError("É necessário aceitar os termos.")
        return v


class NotesBody(BaseModel):
    notes: str | None = Field(default=None, max_length=5000)

    @field_validator("notes", mode="before")
    @classmethod
    def _sanitize(cls, v: Any) -> Any:
        if isinstance(v, str):
            return sanitize_text(v, 5000)
        return v


class AssetOut(BaseModel):
    id: uuid.UUID
    original_filename: str
    mime_type: str
    size_bytes: int
    width: int | None
    height: int | None
    sha256: str
    status: AssetStatus
    has_thumbnail: bool = False
    duplicate_of_existing_file: bool = False

    model_config = {"from_attributes": True}


class AnalysisOut(BaseModel):
    id: uuid.UUID
    provider: str
    model: str
    description: str
    structured_result: dict[str, Any]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewOut(BaseModel):
    id: uuid.UUID
    status: ReviewStatus
    review_notes: str | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SubmissionOut(BaseModel):
    id: uuid.UUID
    public_code: str
    sender_name: str
    sender_email: str
    relationship: str
    photo_date_text: str | None
    date_precision: str | None
    location: str | None
    people: str | None
    story: str | None
    author_name: str | None
    publication_authorized: bool
    terms_accepted: bool
    status: SubmissionStatus
    created_at: datetime
    updated_at: datetime
    assets: list[AssetOut] = []
    analyses: list[AnalysisOut] = []
    reviews: list[ReviewOut] = []

    model_config = {"from_attributes": True}


class SubmissionCreated(BaseModel):
    id: uuid.UUID
    public_code: str
    status: SubmissionStatus
    message: str


class PublicAssetOut(BaseModel):
    id: uuid.UUID
    public_code: str
    photo_date_text: str | None
    date_precision: str | None
    location: str | None
    people: str | None
    story: str | None
    author_name: str | None
    relationship: str | None
    width: int | None
    height: int | None
    media_url: str
    published_at: datetime | None = None


class MilestoneOut(BaseModel):
    id: uuid.UUID
    year: int
    title: str
    summary: str
    source_url: str | None
    source_label: str | None

    model_config = {"from_attributes": True}


class HealthOut(BaseModel):
    status: str
    time: datetime
    role: str


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
