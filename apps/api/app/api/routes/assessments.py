from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models import AssessmentAttempt, AssessmentDefinition, AttemptStatus, User
from app.db.session import get_db
from app.schemas.assessments import (
    AssessmentAttemptResponse,
    CreateAttemptRequest,
    CurrentAssessmentResponse,
    PatchAnswersRequest,
)
from app.schemas.common import MessageResponse
from app.services.assessment_service import (
    get_current_assessment,
    serialize_attempt,
    update_attempt_answers,
)

router = APIRouter()


@router.get("/current", response_model=CurrentAssessmentResponse)
async def current_assessment(db: AsyncSession = Depends(get_db)) -> CurrentAssessmentResponse:
    return CurrentAssessmentResponse.model_validate(await get_current_assessment(db))


@router.post("/attempts", response_model=AssessmentAttemptResponse)
async def create_attempt(
    payload: CreateAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AssessmentAttemptResponse:
    definition = (
        await db.execute(select(AssessmentDefinition).where(AssessmentDefinition.slug == payload.definition_slug))
    ).scalar_one()
    attempt = AssessmentAttempt(
        user_id=current_user.id,
        definition_id=definition.id,
        version=definition.current_version,
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    return AssessmentAttemptResponse.model_validate(await serialize_attempt(db, attempt))


@router.get("/attempts/{attempt_id}", response_model=AssessmentAttemptResponse)
async def get_attempt(
    attempt_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> AssessmentAttemptResponse:
    attempt = (
        await db.execute(
            select(AssessmentAttempt).where(
                AssessmentAttempt.id == uuid.UUID(attempt_id), AssessmentAttempt.user_id == current_user.id
            )
        )
    ).scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado")
    return AssessmentAttemptResponse.model_validate(await serialize_attempt(db, attempt))


@router.patch("/attempts/{attempt_id}/answers", response_model=AssessmentAttemptResponse)
async def patch_answers(
    attempt_id: str,
    payload: PatchAnswersRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AssessmentAttemptResponse:
    attempt = (
        await db.execute(
            select(AssessmentAttempt).where(
                AssessmentAttempt.id == uuid.UUID(attempt_id), AssessmentAttempt.user_id == current_user.id
            )
        )
    ).scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado")
    await update_attempt_answers(db, attempt, payload.answers)
    return AssessmentAttemptResponse.model_validate(await serialize_attempt(db, attempt))


@router.post("/attempts/{attempt_id}/complete", response_model=MessageResponse)
async def complete_attempt(
    attempt_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    attempt = (
        await db.execute(
            select(AssessmentAttempt).where(
                AssessmentAttempt.id == uuid.UUID(attempt_id), AssessmentAttempt.user_id == current_user.id
            )
        )
    ).scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado")
    attempt.status = AttemptStatus.completed
    attempt.progress = 100
    await db.commit()
    return MessageResponse(message="Cuestionario finalizado")
