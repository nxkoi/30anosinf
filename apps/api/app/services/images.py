from __future__ import annotations

import hashlib
import io

from PIL import Image, UnidentifiedImageError

ALLOWED_MIME = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def sniff_image_mime(data: bytes) -> str | None:
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_dimensions(data: bytes) -> tuple[int, int]:
    with Image.open(io.BytesIO(data)) as im:
        return im.width, im.height


def make_thumbnail_webp(data: bytes, max_side: int = 1200, quality: int = 80) -> bytes:
    with Image.open(io.BytesIO(data)) as im:
        im = im.convert("RGB")
        im.thumbnail((max_side, max_side))
        out = io.BytesIO()
        im.save(out, format="WEBP", quality=quality, method=4)
        return out.getvalue()


def validate_image_bytes(data: bytes, max_bytes: int) -> tuple[str, str]:
    if len(data) > max_bytes:
        raise ValueError(f"Arquivo excede o limite de {max_bytes} bytes.")
    if len(data) == 0:
        raise ValueError("Arquivo vazio.")
    mime = sniff_image_mime(data)
    if mime not in ALLOWED_MIME:
        raise ValueError("Formato inválido. Aceitos: JPEG, PNG e WebP.")
    try:
        with Image.open(io.BytesIO(data)) as im:
            im.verify()
    except UnidentifiedImageError as exc:
        raise ValueError("Conteúdo não é uma imagem válida.") from exc
    return mime, ALLOWED_MIME[mime]
