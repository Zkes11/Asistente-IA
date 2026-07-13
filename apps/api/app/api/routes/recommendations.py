from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models import (
    AssessmentAttempt,
    Recommendation,
    RecommendationFeedback,
    RecommendationRun,
    User,
)
from app.db.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.recommendations import (
    FeedbackRequest,
    RecommendationItemResponse,
    RecommendationRunResponse,
)
from app.services.recommendation_engine import generate_recommendations

router = APIRouter()


async def serialize_run(db: AsyncSession, run: RecommendationRun) -> RecommendationRunResponse:
    items = (
        await db.execute(
            select(Recommendation).where(Recommendation.run_id == run.id).order_by(Recommendation.rank)
        )
    ).scalars().all()
    return RecommendationRunResponse(
        id=str(run.id),
        compatibility_score=run.compatibility_score,
        confidence_level=run.confidence_level.value,
        score_components=run.score_components,
        structured_explanation=run.structured_explanation,
        model_version=run.model_version,
        explanation_version=run.explanation_version,
        recommendations=[
            RecommendationItemResponse(
                id=str(item.id),
                program_slug=item.program_slug,
                rank=item.rank,
                compatibility_score=item.compatibility_score,
                confidence_level=item.confidence_level.value,
                triggered_rules=item.triggered_rules,
                supporting_factors=item.supporting_factors,
                development_factors=item.development_factors,
                knowledge_graph_paths=item.knowledge_graph_paths,
            )
            for item in items
        ],
    )


@router.post("/generate", response_model=RecommendationRunResponse)
async def create_recommendations(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> RecommendationRunResponse:
    attempt = (
        await db.execute(
            select(AssessmentAttempt)
            .where(AssessmentAttempt.user_id == current_user.id)
            .order_by(AssessmentAttempt.created_at.desc())
        )
    ).scalars().first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe intento de cuestionario")
    result = await generate_recommendations(db, attempt)
    run = RecommendationRun(
        user_id=current_user.id,
        assessment_attempt_id=attempt.id,
        rule_version=result["rule_version"],
        model_version=result["model_version"],
        assessment_version=attempt.version,
        explanation_version=result["explanation_version"],
        confidence_level=result["confidence_level"],
        compatibility_score=result["compatibility_score"],
        score_components=result["score_components"],
        structured_explanation=result["structured_explanation"],
    )
    db.add(run)
    await db.flush()
    for item in result["recommendations"]:
        db.add(
            Recommendation(
                run_id=run.id,
                user_id=current_user.id,
                program_slug=item["program_slug"],
                rank=item["rank"],
                compatibility_score=item["compatibility_score"],
                confidence_level=result["confidence_level"],
                triggered_rules=item["triggered_rules"],
                supporting_factors=item["supporting_factors"],
                development_factors=item["development_factors"],
                knowledge_graph_paths=item["knowledge_graph_paths"],
            )
        )
    await db.commit()
    await db.refresh(run)
    return await serialize_run(db, run)


@router.get("", response_model=list[RecommendationRunResponse])
async def list_recommendation_runs(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[RecommendationRunResponse]:
    runs = (
        await db.execute(
            select(RecommendationRun)
            .where(RecommendationRun.user_id == current_user.id)
            .order_by(RecommendationRun.created_at.desc())
        )
    ).scalars().all()
    return [await serialize_run(db, run) for run in runs]


@router.get("/{run_id}", response_model=RecommendationRunResponse)
async def get_recommendation_run(
    run_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> RecommendationRunResponse:
    run = (
        await db.execute(
            select(RecommendationRun).where(
                RecommendationRun.id == uuid.UUID(run_id), RecommendationRun.user_id == current_user.id
            )
        )
    ).scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado no encontrado")
    return await serialize_run(db, run)


@router.get("/{run_id}/explanation")
async def get_explanation(
    run_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    run = await get_recommendation_run(run_id, current_user, db)
    return {
        "compatibility_score": run.compatibility_score,
        "confidence_level": run.confidence_level,
        "score_components": run.score_components,
        "recommendations": run.recommendations,
        "model_version": run.model_version,
        "explanation_version": run.explanation_version,
    }


@router.post("/{recommendation_id}/feedback", response_model=MessageResponse)
async def submit_feedback(
    recommendation_id: str,
    payload: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    recommendation = (
        await db.execute(
            select(Recommendation).where(
                Recommendation.id == uuid.UUID(recommendation_id), Recommendation.user_id == current_user.id
            )
        )
    ).scalar_one_or_none()
    if not recommendation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recomendacion no encontrada")
    db.add(
        RecommendationFeedback(
            recommendation_id=recommendation.id,
            user_id=current_user.id,
            helpful=payload.helpful,
            comment=payload.comment,
        )
    )
    await db.commit()
    return MessageResponse(message="Retroalimentacion registrada")
