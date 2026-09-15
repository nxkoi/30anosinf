#!/usr/bin/env python3
"""Collect, organize and document official INF/UFG brand assets for the 30anos project."""

from __future__ import annotations

import hashlib
import html as htmlmod
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CONTENT = ROOT / "content" / "sources"
UA = {"User-Agent": "Mozilla/5.0 (compatible; 30anosinf-asset-collector/1.0; +https://github.com/nxkoi/30anosinf)"}
NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

PAGE_30 = "https://inf.ufg.br/p/manual-da-marca-de-trinta-anos-inf"
PAGE_MANUAL = "https://inf.ufg.br/p/52142-manual-da-marca"
PAGE_MARCA_INF = "https://inf.ufg.br/p/30160-marca-do-inf"
PAGE_CONCURSO = "https://inf.ufg.br/n/premiacao-concurso-selo-comemorativo-instituto-de-informatica-ufg-trinta-anos"
PAGE_CELEBRA = "https://inf.ufg.br/p/62264-instituto-de-informatica-da-ufg-celebra-30-anos-de-historia-e-inovacao"
PAGE_HISTORIA = "https://inf.ufg.br/p/30147-historia-do-inf"
PAGE_PORTAL = "https://inf.ufg.br/"

# Official downloads discovered from HTML of PAGE_30 (not invented).
DOWNLOADS_30 = [
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/marca_30_anos_inf_horizontal_branco_PNG.png",
        "id": "logo-30anos-horizontal-branco",
        "local": "assets/brand/30anos/horizontal/logo-horizontal-branco.png",
        "original_name": "marca_30_anos_inf_horizontal_branco_PNG.png",
        "usage": "Cabeçalho sobre fundo escuro",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/marca_30_anos_inf_horizontal_branco_PDF.pdf",
        "id": "logo-30anos-horizontal-branco-pdf",
        "local": "assets/brand/30anos/horizontal/logo-horizontal-branco.pdf",
        "original_name": "marca_30_anos_inf_horizontal_branco_PDF.pdf",
        "usage": "Versão vetorial/impressão da marca horizontal branca",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/marca_30_anos_inf_horizontal_P_B_PNG.png",
        "id": "logo-30anos-horizontal-pb",
        "local": "assets/brand/30anos/horizontal/logo-horizontal-pb.png",
        "original_name": "marca_30_anos_inf_horizontal_P_B_PNG.png",
        "usage": "Cabeçalho e documentos sobre fundo claro",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/marca_30_anos_inf_horizontal_P_B_PDF.pdf",
        "id": "logo-30anos-horizontal-pb-pdf",
        "local": "assets/brand/30anos/horizontal/logo-horizontal-pb.pdf",
        "original_name": "marca_30_anos_inf_horizontal_P_B_PDF.pdf",
        "usage": "Versão vetorial/impressão da marca horizontal P&B",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/marca_30_anos_inf_horizontal_P_B_JPG.jpg",
        "id": "logo-30anos-horizontal-pb-jpg",
        "local": "assets/brand/30anos/horizontal/logo-horizontal-pb.jpg",
        "original_name": "marca_30_anos_inf_horizontal_P_B_JPG.jpg",
        "usage": "Prévia JPG oficial (preferir PNG quando houver transparência)",
        "kind": "brand_30",
        "page": PAGE_30,
        "note": "JPG oficial listado na página; PNG é preferível para o site",
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/marca_30_anos_inf_vertical_branco_PNG.png",
        "id": "logo-30anos-vertical-branco",
        "local": "assets/brand/30anos/vertical/logo-vertical-branco.png",
        "original_name": "marca_30_anos_inf_vertical_branco_PNG.png",
        "usage": "Peças estreitas ou cards sobre fundo escuro",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/marca_30_anos_inf_vertical_branco_PDF.pdf",
        "id": "logo-30anos-vertical-branco-pdf",
        "local": "assets/brand/30anos/vertical/logo-vertical-branco.pdf",
        "original_name": "marca_30_anos_inf_vertical_branco_PDF.pdf",
        "usage": "Versão vetorial/impressão da marca vertical branca",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/marca_30_anos_inf_vertical_P_B_PNG.png",
        "id": "logo-30anos-vertical-pb",
        "local": "assets/brand/30anos/vertical/logo-vertical-pb.png",
        "original_name": "marca_30_anos_inf_vertical_P_B_PNG.png",
        "usage": "Peças estreitas ou cards sobre fundo claro",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/marca_30_anos_inf_vertical_P_B_PDF.pdf",
        "id": "logo-30anos-vertical-pb-pdf",
        "local": "assets/brand/30anos/vertical/logo-vertical-pb.pdf",
        "original_name": "marca_30_anos_inf_vertical_P_B_PDF.pdf",
        "usage": "Versão vetorial/impressão da marca vertical P&B",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/marca_30_anos_inf_vertical_P_B_JPG.jpg",
        "id": "logo-30anos-vertical-pb-jpg",
        "local": "assets/brand/30anos/vertical/logo-vertical-pb.jpg",
        "original_name": "marca_30_anos_inf_vertical_P_B_JPG.jpg",
        "usage": "Prévia JPG oficial (preferir PNG)",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/SELO_30_anos_inf_branco_PNG.png",
        "id": "selo-30anos-branco",
        "local": "assets/brand/30anos/selo/selo-branco.png",
        "original_name": "SELO_30_anos_inf_branco_PNG.png",
        "usage": "Selo comemorativo sobre fundo escuro",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/SELO_30_anos_inf_branco_PDF.pdf",
        "id": "selo-30anos-branco-pdf",
        "local": "assets/brand/30anos/selo/selo-branco.pdf",
        "original_name": "SELO_30_anos_inf_branco_PDF.pdf",
        "usage": "Versão vetorial/impressão do selo branco",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/SELO_30_anos_inf_P_B_PNG.png",
        "id": "selo-30anos-pb",
        "local": "assets/brand/30anos/selo/selo-pb.png",
        "original_name": "SELO_30_anos_inf_P_B_PNG.png",
        "usage": "Selo comemorativo sobre fundo claro",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/SELO_30_anos_inf_P_B_PDF.pdf",
        "id": "selo-30anos-pb-pdf",
        "local": "assets/brand/30anos/selo/selo-pb.pdf",
        "original_name": "SELO_30_anos_inf_P_B_PDF.pdf",
        "usage": "Versão vetorial/impressão do selo P&B",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/SELO_30_anos_inf_P_B_JPG.jpg",
        "id": "selo-30anos-pb-jpg",
        "local": "assets/brand/30anos/selo/selo-pb.jpg",
        "original_name": "SELO_30_anos_inf_P_B_JPG.jpg",
        "usage": "Prévia JPG oficial do selo P&B (preferir PNG)",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/SELO_30_anos_inf_outline_PNG.png",
        "id": "selo-30anos-outline",
        "local": "assets/brand/30anos/selo/selo-outline.png",
        "original_name": "SELO_30_anos_inf_outline_PNG.png",
        "usage": "Elemento decorativo discreto (contorno)",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/SELO_30_anos_inf_outline_PDF.pdf",
        "id": "selo-30anos-outline-pdf",
        "local": "assets/brand/30anos/selo/selo-outline.pdf",
        "original_name": "SELO_30_anos_inf_outline_PDF.pdf",
        "usage": "Versão vetorial/impressão do selo outline",
        "kind": "brand_30",
        "page": PAGE_30,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/SELO_30_anos_inf_outline_JPG.jpg",
        "id": "selo-30anos-outline-jpg",
        "local": "assets/brand/30anos/selo/selo-outline.jpg",
        "original_name": "SELO_30_anos_inf_outline_JPG.jpg",
        "usage": "Prévia JPG oficial do outline (preferir PNG)",
        "kind": "brand_30",
        "page": PAGE_30,
    },
]

# Extra official asset found on celebration page (may duplicate a selo version).
EXTRA_30 = [
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/selo30.png",
        "id": "selo-30anos-page-celebra",
        "local": "assets/brand/30anos/selo/selo-page-celebra.png",
        "original_name": "selo30.png",
        "usage": "Selo exibido na página comemorativa; comparar hash com versões do manual",
        "kind": "brand_30",
        "page": PAGE_CELEBRA,
    },
]

REFERENCES = [
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/30042026-Pre%CC%82mio-selo-de-30-anos-do-INF_Site-conceito.png",
        "id": "ref-conceito-selo",
        "local": "assets/references/concept/conceito-selo-site.png",
        "original_name": "30042026-Premio-selo-de-30-anos-do-INF_Site-conceito.png",
        "usage": "Referência visual do conceito do selo (não usar como logo do site)",
        "kind": "reference",
        "page": PAGE_CONCURSO,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/30042026_-_Pre%CC%82mio-selo-de-30-anos-do-INF_rascunhos_1.jpg",
        "id": "ref-rascunho-1",
        "local": "assets/references/concept/rascunho-criativo-1.jpg",
        "original_name": "30042026_-_Premio-selo-de-30-anos-do-INF_rascunhos_1.jpg",
        "usage": "Referência do processo criativo (não usar no site público)",
        "kind": "reference",
        "page": PAGE_CONCURSO,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/30042026_-_Pre%CC%82mio-selo-de-30-anos-do-INF_rascunhos_2.jpg",
        "id": "ref-rascunho-2",
        "local": "assets/references/concept/rascunho-criativo-2.jpg",
        "original_name": "30042026_-_Premio-selo-de-30-anos-do-INF_rascunhos_2.jpg",
        "usage": "Referência do processo criativo (não usar no site público)",
        "kind": "reference",
        "page": PAGE_CONCURSO,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/30042026__-_premio_alunos_inf-mokup-01.jpg",
        "id": "ref-mockup-papelaria-01",
        "local": "assets/references/mockups/papelaria-01.jpg",
        "original_name": "30042026__-_premio_alunos_inf-mokup-01.jpg",
        "usage": "Mockup de papelaria — referência de aplicação",
        "kind": "reference",
        "page": PAGE_CONCURSO,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/30042026__-_premio_alunos_inf-mokup-02.jpg",
        "id": "ref-mockup-papelaria-02",
        "local": "assets/references/mockups/papelaria-02.jpg",
        "original_name": "30042026__-_premio_alunos_inf-mokup-02.jpg",
        "usage": "Mockup de papelaria — referência de aplicação",
        "kind": "reference",
        "page": PAGE_CONCURSO,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/WhatsApp_Image_2026-04-29_at_14.54.34_%281%29.jpeg",
        "id": "ref-cerimonia-premiacao",
        "local": "assets/references/concept/cerimonia-premiacao.jpeg",
        "original_name": "WhatsApp_Image_2026-04-29_at_14.54.34_(1).jpeg",
        "usage": "Foto da cerimônia de premiação (referência; não logo)",
        "kind": "reference",
        "page": PAGE_CONCURSO,
    },
]

INF_BRAND = [
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/somente-INF-02.png",
        "id": "logo-inf-somente",
        "local": "assets/brand/inf/logo-inf.png",
        "original_name": "somente-INF-02.png",
        "usage": "Marca INF usada no cabeçalho do portal",
        "kind": "brand_inf",
        "page": PAGE_PORTAL,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/INF_UFG-BRANCA3.svg",
        "id": "logo-inf-ufg-branca-svg",
        "local": "assets/brand/inf/logo-inf-ufg-branca.svg",
        "original_name": "INF_UFG-BRANCA3.svg",
        "usage": "Marca INF/UFG branca (SVG) usada no portal",
        "kind": "brand_inf",
        "page": PAGE_PORTAL,
    },
    {
        "url": "https://inf.ufg.br/up/1218/o/INF_UFG_%281%29.svg",
        "id": "logo-inf-ufg-svg",
        "local": "assets/brand/inf/logo-inf-ufg.svg",
        "original_name": "INF_UFG_(1).svg",
        "usage": "Marca INF/UFG (SVG) no rodapé do portal",
        "kind": "brand_inf",
        "page": PAGE_PORTAL,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1218/o/favicon.png",
        "id": "favicon-inf",
        "local": "assets/brand/inf/favicon.png",
        "original_name": "favicon.png",
        "usage": "Favicon oficial do portal INF",
        "kind": "brand_inf",
        "page": PAGE_PORTAL,
    },
    {
        "url": "http://inf.ufg.br/files/uploads/INF.pdf",
        "id": "marca-inf-pdf",
        "local": "assets/brand/inf/marca-inf.pdf",
        "original_name": "INF.pdf",
        "usage": "Arquivo PDF da marca INF (página Marca do INF)",
        "kind": "brand_inf",
        "page": PAGE_MARCA_INF,
    },
    {
        "url": "http://inf.ufg.br/files/uploads/INF-01.png",
        "id": "marca-inf-01",
        "local": "assets/brand/inf/marca-inf-01.png",
        "original_name": "INF-01.png",
        "usage": "Aplicação da marca INF (variante 01)",
        "kind": "brand_inf",
        "page": PAGE_MARCA_INF,
    },
    {
        "url": "http://inf.ufg.br/files/uploads/INF-02.png",
        "id": "marca-inf-02",
        "local": "assets/brand/inf/marca-inf-02.png",
        "original_name": "INF-02.png",
        "usage": "Aplicação da marca INF (variante 02)",
        "kind": "brand_inf",
        "page": PAGE_MARCA_INF,
    },
    {
        "url": "http://inf.ufg.br/files/uploads/INF-03.png",
        "id": "marca-inf-03",
        "local": "assets/brand/inf/marca-inf-03.png",
        "original_name": "INF-03.png",
        "usage": "Aplicação da marca INF (variante 03)",
        "kind": "brand_inf",
        "page": PAGE_MARCA_INF,
    },
]

UFG_BRAND = [
    {
        "url": "https://files.cercomp.ufg.br/weby/up/1/o/Marca_UFG_Manual_de_uso_vers%C3%A3o_7_6_2022_compressed.pdf",
        "id": "manual-marca-ufg-pdf",
        "local": "assets/brand/ufg/manual-marca-ufg-2022.pdf",
        "original_name": "Marca_UFG_Manual_de_uso_versao_7_6_2022_compressed.pdf",
        "usage": "Manual oficial de uso da marca UFG (PDF)",
        "kind": "brand_ufg",
        "page": PAGE_MANUAL,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/assets/level2/marca-ufg-white-ea3d0f2b1a799089540eacd1929fc973c4d208254d9555d4679b02b32671a51f.svg",
        "id": "logo-ufg-white-svg",
        "local": "assets/brand/ufg/logo-ufg-white.svg",
        "original_name": "marca-ufg-white.svg",
        "usage": "Logo UFG branca (SVG) do template do portal",
        "kind": "brand_ufg",
        "page": PAGE_PORTAL,
    },
    {
        "url": "https://files.cercomp.ufg.br/weby/assets/level2/marca-ufg-677b562915f50ba83e8e1516f068bde65a0e00330471068ad6320189ac9f140a.svg",
        "id": "logo-ufg-color-svg",
        "local": "assets/brand/ufg/logo-ufg.svg",
        "original_name": "marca-ufg.svg",
        "usage": "Logo UFG colorida (SVG) do template do portal",
        "kind": "brand_ufg",
        "page": PAGE_PORTAL,
    },
    {
        "url": "https://inf.ufg.br/up/12/o/UFG_LOGO.png",
        "id": "logo-ufg-png",
        "local": "assets/brand/ufg/logo-ufg.png",
        "original_name": "UFG_LOGO.png",
        "usage": "Logo UFG PNG usada no rodapé do portal INF",
        "kind": "brand_ufg",
        "page": PAGE_PORTAL,
    },
]


def ensure_dirs() -> None:
    for p in [
        ASSETS / "brand/30anos/horizontal",
        ASSETS / "brand/30anos/vertical",
        ASSETS / "brand/30anos/selo",
        ASSETS / "brand/30anos/original",
        ASSETS / "brand/inf",
        ASSETS / "brand/ufg",
        ASSETS / "references/concept",
        ASSETS / "references/mockups",
        ASSETS / "references/screenshots",
        ASSETS / "manifests",
        CONTENT,
    ]:
        p.mkdir(parents=True, exist_ok=True)


def fetch_bytes(url: str, timeout: int = 90) -> tuple[int, str, bytes]:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        return resp.status, ctype, data


def sniff_type(data: bytes, declared: str, url: str) -> tuple[str, bool]:
    """Return (mime, is_valid_binary). Reject HTML error pages."""
    head = data[:256].lstrip().lower()
    if head.startswith(b"<!doctype html") or head.startswith(b"<html") or b"<html" in head[:64]:
        return "text/html", False
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png", True
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg", True
    if data[:4] == b"%PDF":
        return "application/pdf", True
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp", True
    if b"<svg" in data[:500].lower() or data.lstrip().startswith(b"<?xml"):
        if b"<svg" in data.lower():
            return "image/svg+xml", True
    # fallback to declared / extension
    path = urllib.parse.urlparse(url).path.lower()
    if path.endswith(".png"):
        return declared or "image/png", declared.startswith("image/") or not declared
    if path.endswith((".jpg", ".jpeg")):
        return declared or "image/jpeg", True
    if path.endswith(".pdf"):
        return declared or "application/pdf", True
    if path.endswith(".svg"):
        return declared or "image/svg+xml", True
    if declared.startswith(("image/", "application/pdf")):
        return declared, True
    return declared or "application/octet-stream", False


def png_has_transparency(path: Path) -> bool | None:
    if Image is None or path.suffix.lower() != ".png":
        return None
    with Image.open(path) as im:
        if im.mode in ("RGBA", "LA"):
            extrema = im.getextrema()
            alpha = extrema[-1]
            return alpha[0] < 255
        if im.mode == "P":
            return "transparency" in im.info
        return False


def image_size(path: Path) -> tuple[int | None, int | None]:
    if Image is None:
        return None, None
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return None, None
    try:
        with Image.open(path) as im:
            return im.width, im.height
    except Exception:
        return None, None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def hardlink_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def download_item(item: dict, hash_index: dict[str, dict], results: list[dict], failures: list[dict]) -> None:
    url = item["url"]
    print(f"GET {url}")
    try:
        status, ctype, data = fetch_bytes(url)
    except Exception as e:
        failures.append({**item, "status": "failed", "error": str(e)})
        results.append(
            {
                "id": item["id"],
                "file": item["local"],
                "source_url": url,
                "source_page": item["page"],
                "mime_type": None,
                "bytes": None,
                "width": None,
                "height": None,
                "transparent": None,
                "sha256": None,
                "usage": item["usage"],
                "status": "failed",
                "error": str(e),
            }
        )
        return

    mime, ok = sniff_type(data, ctype, url)
    if status >= 400 or not ok:
        failures.append({**item, "status": "failed", "error": f"HTTP {status} or invalid content ({mime})", "declared_ctype": ctype})
        results.append(
            {
                "id": item["id"],
                "file": item["local"],
                "source_url": url,
                "source_page": item["page"],
                "mime_type": mime,
                "bytes": len(data),
                "width": None,
                "height": None,
                "transparent": None,
                "sha256": None,
                "usage": item["usage"],
                "status": "failed",
                "error": f"HTTP {status} or invalid content ({mime})",
            }
        )
        return

    digest = hashlib.sha256(data).hexdigest()
    original_name = item["original_name"]
    # sanitize original filename for filesystem
    safe_original = re.sub(r"[^\w.\-]+", "_", original_name)
    original_path = ASSETS / "brand/30anos/original" / safe_original if item["kind"] == "brand_30" else None

    if digest in hash_index:
        existing = hash_index[digest]
        # reuse physical file; link additional logical paths
        canonical = ROOT / existing["file"]
        target = ROOT / item["local"]
        if target.resolve() != canonical.resolve():
            hardlink_or_copy(canonical, target)
        if original_path and not original_path.exists():
            hardlink_or_copy(canonical, original_path)
        existing.setdefault("also_source_urls", [])
        if url not in existing["also_source_urls"] and url != existing["source_url"]:
            existing["also_source_urls"].append(url)
        existing.setdefault("also_ids", [])
        if item["id"] not in existing["also_ids"] and item["id"] != existing["id"]:
            existing["also_ids"].append(item["id"])
        # If this is a distinct logical placement that isn't the canonical file, record alias entry
        if item["local"] != existing["file"]:
            results.append(
                {
                    "id": item["id"],
                    "file": item["local"],
                    "source_url": url,
                    "source_page": item["page"],
                    "mime_type": existing["mime_type"],
                    "bytes": existing["bytes"],
                    "width": existing.get("width"),
                    "height": existing.get("height"),
                    "transparent": existing.get("transparent"),
                    "sha256": digest,
                    "usage": item["usage"],
                    "status": "duplicate_content",
                    "duplicate_of": existing["id"],
                    "original_preserved": str(original_path.relative_to(ROOT)) if original_path and original_path.exists() else existing.get("original_preserved"),
                }
            )
        else:
            # same logical file requested again; note alternate source
            existing.setdefault("also_source_pages", [])
            if item["page"] not in existing["also_source_pages"]:
                existing["also_source_pages"].append(item["page"])
        return

    # write once to destination
    dest = ROOT / item["local"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)

    if item["kind"] == "brand_30":
        assert original_path is not None
        hardlink_or_copy(dest, original_path)
        original_rel = str(original_path.relative_to(ROOT))
    else:
        # also keep a copy under brand/*/ with simple name already; for INF/UFG/refs store original name alongside
        orig_dir = {
            "brand_inf": ASSETS / "brand/inf/original",
            "brand_ufg": ASSETS / "brand/ufg/original",
            "reference": ASSETS / "references/original",
        }.get(item["kind"])
        original_rel = None
        if orig_dir:
            orig_dir.mkdir(parents=True, exist_ok=True)
            op = orig_dir / safe_original
            hardlink_or_copy(dest, op)
            original_rel = str(op.relative_to(ROOT))

    w, h = image_size(dest)
    transparent = png_has_transparency(dest) if dest.suffix.lower() == ".png" else None

    entry = {
        "id": item["id"],
        "file": item["local"],
        "source_url": url,
        "source_page": item["page"],
        "mime_type": mime,
        "bytes": len(data),
        "width": w,
        "height": h,
        "transparent": transparent,
        "sha256": digest,
        "usage": item["usage"],
        "status": "downloaded",
        "original_preserved": original_rel,
        "kind": item["kind"],
    }
    if item.get("note"):
        entry["note"] = item["note"]
    hash_index[digest] = entry
    results.append(entry)


def take_screenshots(results: list[dict], failures: list[dict]) -> None:
    chromium = shutil.which("chromium") or shutil.which("chromium-browser")
    if not chromium:
        failures.append({"id": "screenshots", "status": "failed", "error": "chromium not found"})
        return

    shots = [
        ("portal-home", PAGE_PORTAL, "Portal INF — página inicial (cabeçalho/navegação)"),
        ("portal-footer", PAGE_PORTAL, "Portal INF — rodapé (rolagem)"),
        ("manual-30anos", PAGE_30, "Página de downloads da marca de 30 anos"),
        ("concurso-selo", PAGE_CONCURSO, "Página do concurso/selo e papelaria"),
        ("manual-marca", PAGE_MANUAL, "Manual da marca INF/UFG"),
        ("marca-inf", PAGE_MARCA_INF, "Aplicações da marca INF"),
        ("historia-inf", PAGE_HISTORIA, "Página História do INF (timeline embutida)"),
        ("celebra-30anos", PAGE_CELEBRA, "Página comemorativa dos 30 anos"),
    ]

    profile = tempfile.mkdtemp(prefix="chromium-30anos-")
    for slug, url, usage in shots:
        out = ASSETS / "references/screenshots" / f"{slug}.png"
        rel = str(out.relative_to(ROOT))
        cmd = [
            chromium,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            f"--user-data-dir={profile}",
            "--window-size=1440,900",
            f"--screenshot={out}",
            url,
        ]
        # For footer, use a taller virtual viewport via CDP is hard; capture full page with virtual time
        if slug == "portal-footer":
            cmd = [
                chromium,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--hide-scrollbars",
                f"--user-data-dir={profile}",
                "--window-size=1440,2400",
                f"--screenshot={out}",
                url,
            ]
        print("SHOT", url, "->", out)
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
            if not out.exists() or out.stat().st_size < 100:
                raise RuntimeError("screenshot file missing or too small")
            digest = sha256_file(out)
            w, h = image_size(out)
            results.append(
                {
                    "id": f"screenshot-{slug}",
                    "file": rel,
                    "source_url": url,
                    "source_page": url,
                    "mime_type": "image/png",
                    "bytes": out.stat().st_size,
                    "width": w,
                    "height": h,
                    "transparent": False,
                    "sha256": digest,
                    "usage": usage + " — apenas referência de design; não publicar",
                    "status": "downloaded",
                    "kind": "screenshot",
                }
            )
        except Exception as e:
            failures.append({"id": f"screenshot-{slug}", "url": url, "status": "failed", "error": str(e)})
            results.append(
                {
                    "id": f"screenshot-{slug}",
                    "file": rel,
                    "source_url": url,
                    "source_page": url,
                    "mime_type": None,
                    "bytes": None,
                    "width": None,
                    "height": None,
                    "transparent": None,
                    "sha256": None,
                    "usage": usage,
                    "status": "failed",
                    "error": str(e),
                    "kind": "screenshot",
                }
            )
    shutil.rmtree(profile, ignore_errors=True)


def strip_html(html: str) -> str:
    html = re.sub(r"<script.*?</script>", "", html, flags=re.S | re.I)
    html = re.sub(r"<style.*?</style>", "", html, flags=re.S | re.I)
    # keep paragraph breaks
    html = re.sub(r"<(br|/p|/h[1-6]|/li)\s*/?>", "\n", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    text = htmlmod.unescape(html)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def extract_article_text(url: str) -> str:
    status, ctype, data = fetch_bytes(url)
    html = data.decode("utf-8", errors="replace")
    # Prefer article body
    m = re.search(r"<article[^>]*>(.*?)</article>", html, flags=re.S | re.I)
    if m:
        body = m.group(1)
    else:
        m = re.search(r'id="content"[^>]*>(.*?)</div>', html, flags=re.S | re.I)
        body = m.group(1) if m else html
    text = strip_html(body)
    # remove common chrome leftovers
    for noise in [
        "Alameda Palmeiras, Quadra D, Câmpus Samambaia",
        "CEP 74690-900 Goiânia - Goiás - Brasil.",
        "Telefone: +55 (62) 3521-1182",
        "Secretaria Acadêmica: Secretaria Administrativa:",
        "(62) 3521-1181 (62) 3521-1501",
    ]:
        text = text.replace(noise, "")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def write_source(filename: str, title: str, url: str, body: str, notes: str | None = None) -> None:
    path = CONTENT / filename
    parts = [
        "---",
        f'title: "{title}"',
        f'source_url: "{url}"',
        f'accessed_at: "{NOW}"',
        'source_type: "official"',
        "---",
        "",
        "## Texto oficial (extraído)",
        "",
        body.strip(),
        "",
    ]
    if notes:
        parts += [
            "## Notas do projeto (não são texto oficial)",
            "",
            notes.strip(),
            "",
        ]
    path.write_text("\n".join(parts), encoding="utf-8")
    print("WROTE", path)


def write_content_sources() -> list[str]:
    written: list[str] = []

    celebra = extract_article_text(PAGE_CELEBRA)
    write_source(
        "celebra-30-anos.md",
        "Instituto de Informática da UFG celebra 30 anos de história e inovação",
        PAGE_CELEBRA,
        celebra,
        notes=(
            "Fonte principal dos marcos 1975, 1983, 1984, 1988, 1996 e 2026.\n"
            "Não foram adicionadas inferências além do texto publicado nesta página."
        ),
    )
    written.append("content/sources/celebra-30-anos.md")

    concurso = extract_article_text(PAGE_CONCURSO)
    write_source(
        "concurso-selo-30-anos.md",
        "Selo Comemorativo Inaugura 30 anos do INF/UFG",
        PAGE_CONCURSO,
        concurso,
        notes=(
            "Contém conceito oficial do selo e autoria (Ana Eliza Bequiman Teixeira e João Vitor Alves de Farias).\n"
            "Observação: o texto oficial da página menciona \"excelência de ensino na área da comunicação\"; "
            "manter a redação oficial sem corrigir."
        ),
    )
    written.append("content/sources/concurso-selo-30-anos.md")

    # History page is mostly an embedded Knight Lab timeline
    hist_html = fetch_bytes(PAGE_HISTORIA)[2].decode("utf-8", errors="replace")
    iframe = re.search(r'<iframe[^>]+src="([^"]+)"', hist_html, flags=re.I)
    iframe_src = htmlmod.unescape(iframe.group(1)) if iframe else None
    article = extract_article_text(PAGE_HISTORIA)
    notes = (
        "A página oficial de História do INF contém pouco texto narrativo no HTML; "
        "o conteúdo principal é uma linha do tempo embutida (Knight Lab Timeline).\n"
        f"URL do embed: {iframe_src or 'não encontrada'}\n"
        "O embed aponta para uma planilha/publicação externa (domínio não-ufg.br). "
        "Por isso os marcos textuais usados no projeto vêm prioritariamente da página comemorativa.\n"
        "Status: informação histórica detalhada da timeline ainda depende de extração futura da fonte do embed, "
        "se houver autorização e confirmação editorial."
    )
    write_source(
        "historia-do-inf.md",
        "História do INF",
        PAGE_HISTORIA,
        article or "(Sem parágrafos narrativos relevantes no HTML da página além do título/endereço.)",
        notes=notes,
    )
    written.append("content/sources/historia-do-inf.md")

    manual30 = extract_article_text(PAGE_30)
    write_source(
        "manual-marca-30-anos.md",
        "Manual da Marca de 30 anos do INF",
        PAGE_30,
        manual30,
        notes=(
            "A própria página oficial indica que o Manual da Marca completo está \"(em construção)\".\n"
            "Estão disponíveis downloads de versões horizontal, vertical e selo (branco, P&B e outline)."
        ),
    )
    written.append("content/sources/manual-marca-30-anos.md")

    # Project synthesis clearly labeled
    synth = CONTENT / "marcos-historicos-resumo-projeto.md"
    synth.write_text(
        "\n".join(
            [
                "---",
                'title: "Marcos históricos — resumo produzido para o projeto"',
                f'source_url: "{PAGE_CELEBRA}"',
                f'accessed_at: "{NOW}"',
                'source_type: "project_summary"',
                "---",
                "",
                "## Atenção",
                "",
                "Este arquivo **não** é texto oficial. É um resumo produzido para o projeto a partir da página "
                f"[comemorativa]({PAGE_CELEBRA}). Cada marco aponta a fonte.",
                "",
                "| Ano | Marco | Classificação | Fonte |",
                "|---|---|---|---|",
                "| 1975 | Criação do Departamento de Estatística e Informática (DEI) no então Instituto de Matemática e Física (IMF) | texto oficial (resumo) | página comemorativa |",
                "| 1983 | Criação do Curso de Bacharelado em Ciências da Computação | texto oficial (resumo) | página comemorativa |",
                "| 1984 | Ingresso da primeira turma | texto oficial (resumo) | página comemorativa |",
                "| 1988 | Reconhecimento do curso pelo Ministério da Educação | texto oficial (resumo) | página comemorativa |",
                "| 1996 | Criação do Instituto de Informática como unidade acadêmica autônoma | texto oficial (resumo) | página comemorativa |",
                "| 2026 | Celebração dos 30 anos do INF | texto oficial (resumo) | página comemorativa / concurso do selo |",
                "",
                "## Ainda não confirmado / pendente",
                "",
                "- Detalhamento completo dos eventos da timeline embutida em https://inf.ufg.br/p/30147-historia-do-inf "
                "(fonte do embed fora de ufg.br).",
                "- Manual completo da marca comemorativa de 30 anos (página oficial: em construção).",
                "",
            ]
        ),
        encoding="utf-8",
    )
    written.append("content/sources/marcos-historicos-resumo-projeto.md")
    return written


def validate_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    for asset in manifest["assets"]:
        if asset.get("status") == "failed":
            continue
        path = ROOT / asset["file"]
        if not path.exists():
            errors.append(f"missing file: {asset['file']}")
            continue
        digest = sha256_file(path)
        if asset.get("sha256") and digest != asset["sha256"]:
            errors.append(f"hash mismatch: {asset['id']} expected {asset['sha256']} got {digest}")
        if asset.get("bytes") is not None and path.stat().st_size != asset["bytes"]:
            errors.append(f"size mismatch: {asset['id']}")
        if asset.get("original_preserved"):
            op = ROOT / asset["original_preserved"]
            if not op.exists():
                errors.append(f"missing original: {asset['original_preserved']}")
            elif sha256_file(op) != digest:
                errors.append(f"original hash differs from working copy: {asset['id']}")
    return errors


def write_readme(manifest: dict, failures: list[dict], content_files: list[str]) -> None:
    ok = [a for a in manifest["assets"] if a.get("status") in ("downloaded", "duplicate_content")]
    brand30 = [a for a in ok if a.get("kind") == "brand_30" or (a["id"].startswith(("logo-30anos", "selo-30anos")) and a.get("status") == "downloaded")]
    # rebuild brand30 from kind field more carefully
    brand30 = [a for a in ok if str(a.get("kind", "")).startswith("brand_30") or a["id"].startswith(("logo-30anos", "selo-30anos"))]
    refs = [a for a in ok if a.get("kind") in ("reference", "screenshot") or a["id"].startswith(("ref-", "screenshot-"))]

    versions = """### Marca 30 anos (página oficial de downloads)

| Versão | PNG | PDF | JPG |
|---|---|---|---|
| Horizontal branca | sim | sim | — |
| Horizontal P&B | sim | sim | sim (prévia) |
| Vertical branca | sim | sim | — |
| Vertical P&B | sim | sim | sim (prévia) |
| Selo branco | sim | sim | — |
| Selo P&B | sim | sim | sim (prévia) |
| Selo outline | sim | sim | sim (prévia) |
"""

    failed_md = "Nenhum." if not failures else "\n".join(
        f"- `{f.get('id', '?')}`: {f.get('error') or f.get('status')} ({f.get('url') or f.get('source_url', '')})"
        for f in failures
    )

    readme = f"""# Assets oficiais — 30 anos INF/UFG

Coleta realizada em `{manifest['generated_at']}` a partir de páginas e arquivos nos domínios `inf.ufg.br`, `files.cercomp.ufg.br` e outros `*.ufg.br`.

## Aviso importante

- A página oficial [Manual da Marca de 30 anos do INF]({PAGE_30}) informa que o **manual completo da marca comemorativa ainda está em construção**.
- **Não recolorir** os arquivos oficiais da marca. Usar somente as versões publicadas (branco, P&B, outline).
- Arquivos em `references/` e `references/screenshots/` são **apenas referência de design** e não devem ir para a versão pública do site sem curadoria.
- Originais oficiais da marca de 30 anos estão preservados sem alteração em `brand/30anos/original/` (hardlinks quando o sistema de arquivos permite).

## Quando usar cada versão

- **Horizontal branca**: cabeçalho sobre fundo escuro.
- **Horizontal P&B**: páginas claras e documentos.
- **Vertical**: peças estreitas ou cards; não como marca principal no desktop.
- **Selo branco / P&B**: destaque comemorativo conforme contraste do fundo.
- **Selo outline**: elemento decorativo discreto.
- **JPG**: apenas prévia oficial; preferir PNG (transparência) ou PDF (vetorial) no site/impressão.
- **Marcas INF/UFG**: rodapé institucional e continuidade com o portal.

{versions}

## Referências (não obrigatórias no site)

Arquivos de conceito, rascunhos, mockups de papelaria e capturas de tela do portal. Ver manifesto (`assets/manifests/assets.json`) com `kind` = `reference` ou `screenshot`.

## Downloads que falharam

{failed_md}

## Itens ainda pendentes / dependem do manual definitivo

- Manual completo da marca comemorativa de 30 anos (status oficial: em construção).
- Paleta cromática oficial definitiva dos 30 anos (hoje só há aproximações a partir das peças).
- Extração editorial completa da timeline embutida em [História do INF]({PAGE_HISTORIA}) (fonte do embed fora de `ufg.br`).
- Eventual publicação de novas variantes da marca após a conclusão do manual.

## Fontes históricas coletadas

Arquivos em `content/sources/`:

{chr(10).join(f'- `{p}`' for p in content_files)}

## Manifesto e relatório

- Manifesto: `assets/manifests/assets.json`
- Relatório desta coleta: `assets/manifests/collection-report.md`

## Estrutura

```text
assets/
├── brand/
│   ├── 30anos/
│   │   ├── horizontal/
│   │   ├── vertical/
│   │   ├── selo/
│   │   └── original/
│   ├── inf/
│   └── ufg/
├── references/
│   ├── concept/
│   ├── mockups/
│   ├── screenshots/
│   └── original/
└── manifests/
```

Total de entradas no manifesto: **{len(manifest['assets'])}** (incluindo falhas e aliases de conteúdo duplicado).
Arquivos baixados com sucesso (status `downloaded`): **{sum(1 for a in manifest['assets'] if a.get('status')=='downloaded')}**.
"""
    (ASSETS / "README.md").write_text(readme, encoding="utf-8")


def write_report(manifest: dict, failures: list[dict], content_files: list[str], validation_errors: list[str], tree: str) -> Path:
    dups = [a for a in manifest["assets"] if a.get("status") == "duplicate_content"]
    also = []
    for a in manifest["assets"]:
        if a.get("also_source_urls") or a.get("also_ids"):
            also.append(a)

    report = ASSETS / "manifests" / "collection-report.md"
    lines = [
        "# Relatório de coleta de assets oficiais",
        "",
        f"- Gerado em: `{manifest['generated_at']}`",
        f"- Manifesto: `assets/manifests/assets.json`",
        f"- README: `assets/README.md`",
        "",
        "## Árvore",
        "",
        "```text",
        tree.rstrip(),
        "```",
        "",
        "## Contagens",
        "",
        f"- Entradas no manifesto: {len(manifest['assets'])}",
        f"- Baixados (`downloaded`): {sum(1 for a in manifest['assets'] if a.get('status')=='downloaded')}",
        f"- Duplicatas de conteúdo (`duplicate_content`): {len(dups)}",
        f"- Falhas: {len(failures)}",
        f"- Fontes históricas: {len(content_files)}",
        "",
        "## Versões da marca 30 anos disponíveis",
        "",
        "- Horizontal: branco (PNG/PDF), P&B (PNG/PDF/JPG)",
        "- Vertical: branco (PNG/PDF), P&B (PNG/PDF/JPG)",
        "- Selo: branco (PNG/PDF), P&B (PNG/PDF/JPG), outline (PNG/PDF/JPG)",
        "",
        "## Downloads que falharam",
        "",
    ]
    if not failures:
        lines.append("Nenhum.")
    else:
        for f in failures:
            lines.append(f"- `{f.get('id')}`: {f.get('error')} — {f.get('url') or f.get('source_url','')}")

    lines += ["", "## Arquivos potencialmente duplicados", ""]
    if not dups and not also:
        lines.append("Nenhuma duplicata de conteúdo detectada por SHA-256.")
    else:
        for a in dups:
            lines.append(f"- `{a['id']}` aponta para o mesmo conteúdo de `{a.get('duplicate_of')}` (SHA-256 `{a['sha256']}`).")
        for a in also:
            if a.get("also_source_urls"):
                lines.append(f"- `{a['id']}` também encontrado em: {', '.join(a['also_source_urls'])}")

    lines += ["", "## Fontes históricas coletadas", ""]
    for p in content_files:
        lines.append(f"- `{p}`")

    lines += [
        "",
        "## Itens pendentes",
        "",
        "- Manual completo da marca de 30 anos (em construção na página oficial).",
        "- Paleta oficial definitiva dos 30 anos.",
        "- Conteúdo detalhado da timeline de História do INF (embed externo).",
        "",
        "## Validação automática",
        "",
    ]
    if validation_errors:
        lines.append("Falhas de validação:")
        for e in validation_errors:
            lines.append(f"- {e}")
    else:
        lines.append("Todos os hashes, tamanhos e originais referenciados no manifesto foram validados com sucesso.")

    lines += [
        "",
        "## Confirmação de escopo",
        "",
        "**Nenhuma página do site foi implementada nesta etapa.** Não foram criados componentes, CSS, Docker Compose de aplicação nem páginas Astro/HTML do site público.",
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def directory_tree() -> str:
    cmd = ["find", str(ASSETS), str(CONTENT), "-print"]
    out = subprocess.check_output(cmd, text=True)
    paths = sorted(out.strip().splitlines())
    # render simple tree-ish list relative to ROOT
    lines = []
    for p in paths:
        rel = str(Path(p).relative_to(ROOT))
        lines.append(rel)
    return "\n".join(lines)


def main() -> int:
    ensure_dirs()
    results: list[dict] = []
    failures: list[dict] = []
    hash_index: dict[str, dict] = {}

    all_items = DOWNLOADS_30 + EXTRA_30 + REFERENCES + INF_BRAND + UFG_BRAND
    for item in all_items:
        download_item(item, hash_index, results, failures)

    take_screenshots(results, failures)
    content_files = write_content_sources()

    # Normalize: ensure kind present
    for a in results:
        a.setdefault("kind", "other")

    manifest = {
        "generated_at": NOW,
        "project": "30anosinf",
        "source_domains": ["inf.ufg.br", "files.cercomp.ufg.br", "ufg.br"],
        "notes": [
            "Manual completo da marca comemorativa ainda em construção na página oficial.",
            "Arquivos oficiais não devem ser recoloridos.",
            "Screenshots e referências não devem ser usados diretamente no site público.",
        ],
        "assets": results,
        "failures": [
            {"id": f.get("id"), "error": f.get("error"), "url": f.get("url") or f.get("source_url")}
            for f in failures
        ],
        "content_sources": content_files,
    }

    manifest_path = ASSETS / "manifests" / "assets.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    validation_errors = validate_manifest(manifest)
    tree = directory_tree()
    write_readme(manifest, failures, content_files)
    report = write_report(manifest, failures, content_files, validation_errors, tree)

    # summary validation file
    (ASSETS / "manifests" / "validation.json").write_text(
        json.dumps(
            {
                "validated_at": NOW,
                "ok": not validation_errors,
                "errors": validation_errors,
                "downloaded": sum(1 for a in results if a.get("status") == "downloaded"),
                "failed": len(failures),
                "duplicate_content": sum(1 for a in results if a.get("status") == "duplicate_content"),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("\n=== SUMMARY ===")
    print("manifest:", manifest_path)
    print("report:", report)
    print("downloaded:", sum(1 for a in results if a.get("status") == "downloaded"))
    print("duplicates:", sum(1 for a in results if a.get("status") == "duplicate_content"))
    print("failed:", len(failures))
    print("validation_errors:", validation_errors)
    return 0 if not validation_errors else 1


if __name__ == "__main__":
    sys.exit(main())
