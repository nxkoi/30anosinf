from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import get_settings

security = HTTPBasic()


def require_review_auth(
    credentials: HTTPBasicCredentials = Depends(security),
) -> str:
    settings = get_settings()
    user_ok = secrets.compare_digest(credentials.username, settings.review_username)
    pass_ok = secrets.compare_digest(credentials.password, settings.review_password)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
