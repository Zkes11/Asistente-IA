from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models import AcademicProgram, FavoriteProgram, User
from app.db.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.programs import ProgramCompareRequest, ProgramResponse

router = APIRouter()


def serialize_program(program: AcademicProgram) -> ProgramResponse:
    return ProgramResponse(
        slug=program.slug,
        name=program.name,
        short_description=program.short_description,
        academic_area_slug=program.academic_area_slug,
        metadata_json=program.metadata_json,
        source_name=program.source_name,
        source_url=program.source_url,
        verified_at=program.verified_at.isoformat() if program.verified_at else None,
    )


@router.get("", response_model=list[ProgramResponse])
async def list_programs(db: AsyncSession = Depends(get_db)) -> list[ProgramResponse]:
    programs = (await db.execute(select(AcademicProgram).order_by(AcademicProgram.name))).scalars().all()
    return [serialize_program(program) for program in programs]


@router.get("/{slug}", response_model=ProgramResponse)
async def get_program(slug: str, db: AsyncSession = Depends(get_db)) -> ProgramResponse:
    program = (
        await db.execute(select(AcademicProgram).where(AcademicProgram.slug == slug))
    ).scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programa no encontrado")
    return serialize_program(program)


@router.post("/compare", response_model=list[ProgramResponse])
async def compare_programs(payload: ProgramCompareRequest, db: AsyncSession = Depends(get_db)) -> list[ProgramResponse]:
    programs = (
        await db.execute(select(AcademicProgram).where(AcademicProgram.slug.in_(payload.slugs)))
    ).scalars().all()
    return [serialize_program(program) for program in programs]


@router.post("/{slug}/favorite", response_model=MessageResponse)
async def favorite_program(
    slug: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    program = (
        await db.execute(select(AcademicProgram).where(AcademicProgram.slug == slug))
    ).scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programa no encontrado")
    favorite = FavoriteProgram(user_id=current_user.id, program_slug=slug)
    db.add(favorite)
    await db.commit()
    return MessageResponse(message="Programa guardado")


@router.delete("/{slug}/favorite", response_model=MessageResponse)
async def unfavorite_program(
    slug: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    await db.execute(
        delete(FavoriteProgram).where(
            FavoriteProgram.user_id == current_user.id, FavoriteProgram.program_slug == slug
        )
    )
    await db.commit()
    return MessageResponse(message="Programa eliminado de guardados")
