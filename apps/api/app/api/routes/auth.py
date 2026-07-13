from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.models import RefreshToken, Role, RoleName, User, UserProfile, UserRole
from app.db.session import get_db
from app.schemas.auth import AuthUserResponse, LoginRequest, RegisterRequest, TokenResponse
from app.schemas.common import MessageResponse
from app.security.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.security.passwords import hash_password, verify_password

router = APIRouter()


def token_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@router.post("/register", response_model=AuthUserResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> AuthUserResponse:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Correo ya registrado")
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        preferred_name=payload.preferred_name,
    )
    profile = UserProfile(user=user)
    role = (await db.execute(select(Role).where(Role.name == RoleName.student))).scalar_one()
    db.add_all([user, profile, UserRole(user=user, role=role)])
    await db.commit()
    await db.refresh(user)
    return AuthUserResponse(id=str(user.id), email=user.email, preferred_name=user.preferred_name)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    result = await db.execute(
        select(User).options(selectinload(User.roles).selectinload(UserRole.role)).where(User.email == payload.email)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=token_hash(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(days=14),
        )
    )
    await db.commit()
    response.set_cookie("orientaia_access_token", access_token, httponly=True, samesite="lax")
    response.set_cookie("orientaia_refresh_token", refresh_token, httponly=True, samesite="lax")
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    refresh_token = request.cookies.get("orientaia_refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token ausente")
    try:
        payload = decode_refresh_token(refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido") from exc
    stored = (
        await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash(refresh_token)))
    ).scalar_one_or_none()
    if not stored or stored.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revocado")
    stored.revoked_at = datetime.now(UTC)
    new_access = create_access_token(str(payload["sub"]))
    new_refresh = create_refresh_token(str(payload["sub"]))
    db.add(
        RefreshToken(
            user_id=stored.user_id,
            token_hash=token_hash(new_refresh),
            expires_at=datetime.now(UTC) + timedelta(days=14),
        )
    )
    await db.commit()
    response.set_cookie("orientaia_access_token", new_access, httponly=True, samesite="lax")
    response.set_cookie("orientaia_refresh_token", new_refresh, httponly=True, samesite="lax")
    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response) -> MessageResponse:
    response.delete_cookie("orientaia_access_token")
    response.delete_cookie("orientaia_refresh_token")
    return MessageResponse(message="Sesion cerrada")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> MessageResponse:
    tokens = (await db.execute(select(RefreshToken).where(RefreshToken.user_id == current_user.id))).scalars().all()
    now = datetime.now(UTC)
    for token in tokens:
        token.revoked_at = now
    await db.commit()
    return MessageResponse(message="Todas las sesiones fueron cerradas")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password() -> MessageResponse:
    return MessageResponse(message="Si el correo existe, recibira instrucciones de recuperacion.")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password() -> MessageResponse:
    return MessageResponse(message="Flujo preparado para adaptador de correo local.")


@router.get("/me", response_model=AuthUserResponse)
async def me(current_user: User = Depends(get_current_user)) -> AuthUserResponse:
    return AuthUserResponse(
        id=str(current_user.id), email=current_user.email, preferred_name=current_user.preferred_name
    )
