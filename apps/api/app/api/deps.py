from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import RoleName, User
from app.db.session import get_db
from app.security.jwt import decode_access_token
from app.security.passwords import hash_password
from app.db.models import Role, UserProfile, UserRole


async def get_or_create_demo_user(db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.email == settings.demo_user_email, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()
    if user:
        return user

    role = (await db.execute(select(Role).where(Role.name == RoleName.student))).scalar_one_or_none()
    if role is None:
        role = Role(name=RoleName.student)
        db.add(role)
        await db.flush()

    user = User(
        email=settings.demo_user_email,
        password_hash=hash_password("demo-orientaia-123"),
        preferred_name=settings.demo_user_name,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    db.add(
        UserProfile(
            user_id=user.id,
            goal="explorar",
            known_areas=[],
            onboarding_completed=True,
            privacy_policy_accepted=True,
            assessment_consent=True,
        )
    )
    db.add(UserRole(user_id=user.id, role_id=role.id))
    await db.commit()
    await db.refresh(user)
    return user


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    token = request.cookies.get("orientaia_access_token")
    if not token:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ").strip()
    if not token and settings.single_user_mode:
        return await get_or_create_demo_user(db)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    try:
        payload = decode_access_token(token)
        user_id = uuid.UUID(str(payload["sub"]))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido") from exc
    result = await db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    role_names = {role.role.name for role in user.roles}
    if RoleName.admin not in role_names:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    return user
