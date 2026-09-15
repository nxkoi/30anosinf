from __future__ import annotations

import io
import time
import uuid

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# These tests run inside the api container against the real stack.


@pytest.fixture(scope="session")
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def auth():
    import os

    user = os.environ.get("REVIEW_USERNAME", "revisao")
    password = os.environ.get("REVIEW_PASSWORD", "revisao-trocar")
    return (user, password)


def _png(color=(10, 20, 30), size=(120, 80)) -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_upload_complete_and_process(client, auth):
    payload = {
        "sender_name": "Teste Automatizado",
        "sender_email": "teste@example.com",
        "relationship": "Estudante",
        "photo_date_text": "2020",
        "date_precision": "ano",
        "location": "Samambaia",
        "people": "A e B",
        "story": "Relato de teste",
        "author_name": "Fotógrafo",
        "publication_authorized": True,
        "terms_accepted": True,
    }
    r = client.post("/api/submissions", json=payload)
    assert r.status_code == 201, r.text
    sub = r.json()
    assert sub["public_code"].startswith("SUB-")

    png = _png()
    files = {"file": ("foto.png", png, "image/png")}
    r = client.post(f"/api/submissions/{sub['id']}/files", files=files)
    assert r.status_code == 201, r.text
    asset = r.json()
    assert asset["sha256"]
    assert asset["duplicate_of_existing_file"] is False

    # exact dedup second upload same bytes on new submission
    r2 = client.post("/api/submissions", json={**payload, "sender_email": "outro@example.com"})
    sub2 = r2.json()
    r = client.post(f"/api/submissions/{sub2['id']}/files", files={"file": ("foto2.png", png, "image/png")})
    assert r.status_code == 201
    assert r.json()["duplicate_of_existing_file"] is True
    assert r.json()["sha256"] == asset["sha256"]

    r = client.post(f"/api/submissions/{sub['id']}/complete")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "QUEUED"

    # wait worker
    ready = None
    for _ in range(40):
        time.sleep(0.5)
        rr = client.get(f"/api/review/submissions/{sub['id']}", auth=auth)
        if rr.status_code == 200 and rr.json()["status"] == "READY_FOR_REVIEW":
            ready = rr.json()
            break
    assert ready is not None, "worker did not finish in time"
    assert ready["assets"][0]["has_thumbnail"] is True
    assert ready["analyses"]
    assert "Descrição automática ainda não disponível" in ready["analyses"][0]["description"]


def test_reject_invalid_format_and_size(client):
    r = client.post(
        "/api/submissions",
        json={
            "sender_name": "X Y",
            "sender_email": "xy@example.com",
            "relationship": "Egresso(a)",
            "publication_authorized": False,
            "terms_accepted": True,
        },
    )
    sub_id = r.json()["id"]
    r = client.post(
        f"/api/submissions/{sub_id}/files",
        files={"file": ("x.txt", b"not-an-image", "text/plain")},
    )
    assert r.status_code == 400

    big = b"\xff\xd8\xff" + b"0" * (21 * 1024 * 1024)
    r = client.post(
        f"/api/submissions/{sub_id}/files",
        files={"file": ("big.jpg", big, "image/jpeg")},
    )
    assert r.status_code == 400


def test_review_auth_and_publish_rules(client, auth):
    r = client.get("/api/review/submissions")
    assert r.status_code == 401

    # create unauthorized publication submission
    payload = {
        "sender_name": "Sem Autorizacao",
        "sender_email": "noauth@example.com",
        "relationship": "Docente",
        "publication_authorized": False,
        "terms_accepted": True,
        "story": "não autorizo",
    }
    sub = client.post("/api/submissions", json=payload).json()
    png = _png(color=(200, 100, 50), size=(100, 60))
    client.post(f"/api/submissions/{sub['id']}/files", files={"file": ("a.png", png, "image/png")})
    client.post(f"/api/submissions/{sub['id']}/complete")

    ready = None
    for _ in range(40):
        time.sleep(0.5)
        rr = client.get(f"/api/review/submissions/{sub['id']}", auth=auth)
        if rr.status_code == 200 and rr.json()["status"] == "READY_FOR_REVIEW":
            ready = rr.json()
            break
    assert ready

    assert client.post(f"/api/review/submissions/{sub['id']}/approve", auth=auth).status_code == 200
    pub = client.post(f"/api/review/submissions/{sub['id']}/publish", auth=auth)
    assert pub.status_code == 400
    assert "autoriz" in pub.json()["detail"].lower()

    # authorized path
    payload["sender_email"] = f"ok-{uuid.uuid4().hex[:8]}@example.com"
    payload["publication_authorized"] = True
    sub = client.post("/api/submissions", json=payload).json()
    png = _png(color=(20, 180, 90), size=(110, 70))
    client.post(f"/api/submissions/{sub['id']}/files", files={"file": ("b.png", png, "image/png")})
    client.post(f"/api/submissions/{sub['id']}/complete")
    for _ in range(40):
        time.sleep(0.5)
        rr = client.get(f"/api/review/submissions/{sub['id']}", auth=auth)
        if rr.status_code == 200 and rr.json()["status"] == "READY_FOR_REVIEW":
            break
    assert client.post(f"/api/review/submissions/{sub['id']}/approve", auth=auth).status_code == 200
    assert client.post(f"/api/review/submissions/{sub['id']}/publish", auth=auth).status_code == 200

    asset_id = client.get(f"/api/review/submissions/{sub['id']}", auth=auth).json()["assets"][0]["id"]
    public_list = client.get("/api/public/assets").json()
    assert any(a["id"] == asset_id for a in public_list)
    assert client.get(f"/api/public/assets/{asset_id}").status_code == 200
    assert client.get(f"/api/public/assets/{asset_id}/media").status_code == 200

    # unpublished remains invisible: create another ready item and ensure not listed
    payload["sender_email"] = f"hide-{uuid.uuid4().hex[:8]}@example.com"
    hidden = client.post("/api/submissions", json=payload).json()
    client.post(
        f"/api/submissions/{hidden['id']}/files",
        files={"file": ("c.png", _png(color=(1, 2, 3), size=(90, 90)), "image/png")},
    )
    client.post(f"/api/submissions/{hidden['id']}/complete")
    for _ in range(40):
        time.sleep(0.5)
        rr = client.get(f"/api/review/submissions/{hidden['id']}", auth=auth)
        if rr.status_code == 200 and rr.json()["status"] == "READY_FOR_REVIEW":
            break
    hidden_asset = client.get(f"/api/review/submissions/{hidden['id']}", auth=auth).json()["assets"][0]["id"]
    public_ids = {a["id"] for a in client.get("/api/public/assets").json()}
    assert hidden_asset not in public_ids
