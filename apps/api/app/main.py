from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import public, review, submissions
from app.schemas import HealthOut

settings = get_settings()

app = FastAPI(
    title="Acervo 30 anos INF/UFG",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(submissions.router, prefix="/api")
app.include_router(review.router, prefix="/api")
app.include_router(public.router, prefix="/api")


@app.get("/api/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok", time=datetime.now(timezone.utc), role=settings.app_role)
