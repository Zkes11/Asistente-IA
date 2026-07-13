from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt

from app.core.config import settings


def create_access_token(subject: str) -> str:
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": datetime.now(UTC) + expires_delta}
    return str(jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256"))


def create_refresh_token(subject: str) -> str:
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, Any] = {"sub": subject, "exp": datetime.now(UTC) + expires_delta}
    return str(jwt.encode(payload, settings.jwt_refresh_secret_key, algorithm="HS256"))


def decode_access_token(token: str) -> dict[str, Any]:
    return dict(jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"]))


def decode_refresh_token(token: str) -> dict[str, Any]:
    return dict(jwt.decode(token, settings.jwt_refresh_secret_key, algorithms=["HS256"]))
