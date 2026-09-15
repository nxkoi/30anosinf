from __future__ import annotations

import io
from functools import lru_cache

from minio import Minio
from minio.error import S3Error

from app.config import get_settings


@lru_cache
def get_minio() -> Minio:
    s = get_settings()
    return Minio(
        s.minio_endpoint,
        access_key=s.minio_root_user,
        secret_key=s.minio_root_password,
        secure=s.minio_secure,
        region=s.minio_region,
    )


def put_bytes(bucket: str, key: str, data: bytes, content_type: str) -> None:
    client = get_minio()
    client.put_object(
        bucket,
        key,
        io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )


def get_bytes(bucket: str, key: str) -> bytes:
    client = get_minio()
    response = client.get_object(bucket, key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def copy_object(src_bucket: str, src_key: str, dst_bucket: str, dst_key: str) -> None:
    from minio.commonconfig import CopySource

    client = get_minio()
    client.copy_object(dst_bucket, dst_key, CopySource(src_bucket, src_key))


def object_exists(bucket: str, key: str) -> bool:
    client = get_minio()
    try:
        client.stat_object(bucket, key)
        return True
    except S3Error:
        return False


def find_existing_object_by_sha(sha256: str) -> tuple[str, str] | None:
    """Return (bucket, key) if an object already stored with this sha in quarantine or originals.

    The key convention is ``{sha256[:2]}/{sha256}/{uuid}.{ext}`` — we scan metadata via DB instead.
    This helper is unused for listing; callers use DB asset rows.
    """
    return None
