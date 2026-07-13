from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import University
from app.db.session import get_db

router = APIRouter()


@router.get("")
async def list_universities(db: AsyncSession = Depends(get_db)) -> list[dict[str, object | None]]:
    universities = (await db.execute(select(University).order_by(University.name))).scalars().all()
    return [
        {
            "slug": university.slug,
            "name": university.name,
            "city": university.city,
            "country": university.country,
            "is_demo_data": university.is_demo_data,
            "source_name": university.source_name,
            "verified_at": university.verified_at.isoformat() if university.verified_at else None,
        }
        for university in universities
    ]


@router.get("/{slug}")
async def get_university(slug: str, db: AsyncSession = Depends(get_db)) -> dict[str, object | None]:
    university = (
        await db.execute(select(University).where(University.slug == slug))
    ).scalar_one_or_none()
    if not university:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Universidad no encontrada")
    return {
        "slug": university.slug,
        "name": university.name,
        "city": university.city,
        "country": university.country,
        "is_demo_data": university.is_demo_data,
        "source_name": university.source_name,
        "source_url": university.source_url,
        "verified_at": university.verified_at.isoformat() if university.verified_at else None,
        "warning": "Datos de demostracion",
    }
