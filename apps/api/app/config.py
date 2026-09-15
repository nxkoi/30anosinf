from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://acervo:acervo@postgres:5432/acervo30"
    redis_url: str = "redis://redis:6379/0"

    minio_endpoint: str = "minio:9000"
    minio_root_user: str = "minioadmin"
    minio_root_password: str = "minioadmin"
    minio_secure: bool = False
    minio_region: str = "us-east-1"

    bucket_quarantine: str = "submissions-quarantine"
    bucket_originals: str = "originals"
    bucket_derived: str = "derived"
    bucket_approved: str = "approved-assets"

    review_username: str = "revisao"
    review_password: str = "changeme"

    max_upload_bytes: int = 20 * 1024 * 1024
    max_files_per_submission: int = 10

    api_cors_origins: str = "http://localhost,http://127.0.0.1"
    image_provider: str = "mock"
    llm_provider: str = "mock"
    app_role: str = "api"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
