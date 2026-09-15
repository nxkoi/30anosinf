#!/usr/bin/env python3
"""Seed milestones and a demo submission ready for review (not published)."""

from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone

from PIL import Image
from sqlalchemy import select

from app.config import get_settings
from app.db import (
    Analysis,
    Asset,
    AssetStatus,
    Milestone,
    Review,
    ReviewStatus,
    Submission,
    SubmissionStatus,
)
from app.services.audit import audit
from app.services.codes import next_public_code
from app.services.images import make_thumbnail_webp, sha256_bytes
from app.session import SessionLocal
from app.storage import put_bytes

SOURCE = "https://inf.ufg.br/p/62264-instituto-de-informatica-da-ufg-celebra-30-anos-de-historia-e-inovacao"

MILESTONES = [
    (1975, "Criação do DEI", "Criação do Departamento de Estatística e Informática (DEI) no então Instituto de Matemática e Física (IMF).", 1),
    (1983, "Criação do curso", "Criação do Curso de Bacharelado em Ciências da Computação.", 2),
    (1984, "Primeira turma", "Ingresso da primeira turma do curso de Ciências da Computação.", 3),
    (1988, "Reconhecimento do curso", "Reconhecimento do curso pelo Ministério da Educação.", 4),
    (1996, "Criação do INF", "Criação do Instituto de Informática como unidade acadêmica autônoma da UFG.", 5),
    (2026, "30 anos do INF", "Celebração dos 30 anos do Instituto de Informática.", 6),
]


def make_demo_png() -> bytes:
    img = Image.new("RGB", (640, 480), color=(16, 35, 75))
    # simple pattern — not a historical photo; labeled as demo
    for x in range(0, 640, 40):
        for y in range(0, 480, 40):
            if (x // 40 + y // 40) % 2 == 0:
                for dx in range(20):
                    for dy in range(20):
                        img.putpixel((x + dx, y + dy), (80, 55, 230))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        for year, title, summary, order in MILESTONES:
            exists = db.execute(
                select(Milestone).where(Milestone.year == year, Milestone.title == title)
            ).scalar_one_or_none()
            if exists:
                continue
            db.add(
                Milestone(
                    year=year,
                    title=title,
                    summary=summary,
                    source_url=SOURCE,
                    source_label="Página comemorativa INF",
                    sort_order=order,
                )
            )
        db.commit()

        demo = db.execute(
            select(Submission).where(Submission.public_code.like("SUB-%")).limit(1)
        ).scalar_one_or_none()
        # Only create demo if none exists with sender Demo Seed
        demo = db.execute(
            select(Submission).where(Submission.sender_email == "demo.seed@example.invalid")
        ).scalar_one_or_none()
        if demo is None:
            code = next_public_code(db)
            sub = Submission(
                public_code=code,
                sender_name="Demonstração Seed",
                sender_email="demo.seed@example.invalid",
                relation="Equipe do projeto (demonstração)",
                photo_date_text="2026",
                date_precision="ano",
                location="Laboratório de demonstração",
                people="—",
                story=(
                    "Submissão de demonstração gerada por make seed. "
                    "Não é uma fotografia histórica. Disponível para revisão; "
                    "não publicada automaticamente."
                ),
                author_name="Seed automático",
                publication_authorized=True,
                terms_accepted=True,
                status=SubmissionStatus.READY_FOR_REVIEW,
            )
            db.add(sub)
            db.flush()

            png = make_demo_png()
            digest = sha256_bytes(png)
            object_key = f"{digest[:2]}/{digest}/{uuid.uuid4().hex}.png"
            put_bytes(settings.bucket_quarantine, object_key, png, "image/png")
            put_bytes(settings.bucket_originals, object_key, png, "image/png")

            asset = Asset(
                submission_id=sub.id,
                original_filename="demo-seed.png",
                object_key=object_key,
                sha256=digest,
                mime_type="image/png",
                size_bytes=len(png),
                width=640,
                height=480,
                status=AssetStatus.READY,
            )
            db.add(asset)
            db.flush()

            thumb = make_thumbnail_webp(png)
            derived_key = f"{digest[:2]}/{digest}/{asset.id}.webp"
            put_bytes(settings.bucket_derived, derived_key, thumb, "image/webp")
            asset.derived_key = derived_key

            db.add(
                Analysis(
                    asset_id=asset.id,
                    provider="mock",
                    model="mock-image-v0",
                    description=(
                        "Descrição automática ainda não disponível. "
                        "A imagem foi recebida e preparada para integração futura com a API multimodal."
                    ),
                    structured_result={"seed": True, "inference": True, "confidence": 0.0},
                    status="DONE",
                )
            )
            db.add(Review(submission_id=sub.id, status=ReviewStatus.PENDING, review_notes="Seed demo"))
            audit(
                db,
                entity_type="submission",
                entity_id=sub.id,
                action="seed_created",
                details={"public_code": code, "published": False},
            )
            db.commit()
            print(f"Seed OK — demo submission {code} ready for review (not published).")
        else:
            print(f"Seed OK — demo already exists: {demo.public_code}")
        print("Milestones ensured.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
