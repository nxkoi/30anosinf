"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "submission_counters",
        sa.Column("year", sa.Integer(), primary_key=True),
        sa.Column("last_value", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "milestones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(500)),
        sa.Column("source_label", sa.String(200)),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("year", "title", name="uq_milestone_year_title"),
    )
    op.create_index("ix_milestones_year", "milestones", ["year"])

    submission_status = sa.Enum(
        "RECEIVED",
        "QUEUED",
        "PROCESSING",
        "READY_FOR_REVIEW",
        "CHANGES_REQUESTED",
        "APPROVED",
        "REJECTED",
        "PUBLISHED",
        "ERROR",
        name="submission_status",
    )
    asset_status = sa.Enum(
        "UPLOADED",
        "PROCESSING",
        "READY",
        "APPROVED",
        "REJECTED",
        "PUBLISHED",
        "ERROR",
        name="asset_status",
    )
    review_status = sa.Enum(
        "PENDING",
        "APPROVED",
        "CHANGES_REQUESTED",
        "REJECTED",
        "PUBLISHED",
        name="review_status",
    )
    op.create_table(
        "submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("public_code", sa.String(32), nullable=False),
        sa.Column("sender_name", sa.String(200), nullable=False),
        sa.Column("sender_email", sa.String(320), nullable=False),
        sa.Column("relationship", sa.String(200), nullable=False),
        sa.Column("photo_date_text", sa.String(200)),
        sa.Column("date_precision", sa.String(50)),
        sa.Column("location", sa.String(300)),
        sa.Column("people", sa.Text()),
        sa.Column("story", sa.Text()),
        sa.Column("author_name", sa.String(200)),
        sa.Column("publication_authorized", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("terms_accepted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("status", submission_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("public_code"),
    )
    op.create_index("ix_submissions_public_code", "submissions", ["public_code"])
    op.create_index("ix_submissions_status", "submissions", ["status"])

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("submissions.id", ondelete="CASCADE")),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("object_key", sa.String(500), nullable=False),
        sa.Column("derived_key", sa.String(500)),
        sa.Column("approved_key", sa.String(500)),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("width", sa.Integer()),
        sa.Column("height", sa.Integer()),
        sa.Column("status", asset_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_assets_submission_id", "assets", ["submission_id"])
    op.create_index("ix_assets_sha256", "assets", ["sha256"])
    op.create_index("ix_assets_object_key", "assets", ["object_key"])
    op.create_index("ix_assets_status", "assets", ["status"])

    op.create_table(
        "analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="CASCADE")),
        sa.Column("provider", sa.String(100), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("structured_result", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(50), nullable=False, server_default="DONE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_analyses_asset_id", "analyses", ["asset_id"])

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("submission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("submissions.id", ondelete="CASCADE")),
        sa.Column("status", review_status, nullable=False),
        sa.Column("review_notes", sa.Text()),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_reviews_submission_id", "reviews", ["submission_id"])

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_events_entity_type", "audit_events", ["entity_type"])
    op.create_index("ix_audit_events_entity_id", "audit_events", ["entity_id"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("reviews")
    op.drop_table("analyses")
    op.drop_table("assets")
    op.drop_table("submissions")
    op.drop_table("milestones")
    op.drop_table("submission_counters")
    sa.Enum(name="review_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="asset_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="submission_status").drop(op.get_bind(), checkfirst=True)
