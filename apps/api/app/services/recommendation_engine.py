from __future__ import annotations

from collections import defaultdict
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import AcademicProgram, AssessmentAnswer, AssessmentAttempt, ConfidenceLevel
from app.services.graph import score_graph
from app.services.ml import score_ml
from app.services.rules import score_rules

QUESTION_FEATURE_MAP = {
    "interest_technology": "interest_technology",
    "interest_social": "interest_social",
    "interest_design": "interest_design",
    "interest_health": "interest_health",
    "interest_business": "interest_business",
    "interest_data": "interest_data",
    "logical_reasoning": "logical_reasoning",
    "communication": "communication",
    "empathy": "empathy",
    "creativity": "creativity",
    "numerical_skill": "numerical_skill",
    "visual_thinking": "visual_thinking",
    "organization": "organization",
    "teamwork_preference": "teamwork_preference",
    "autonomy_preference": "autonomy_preference",
    "practical_learning": "practical_learning",
    "theoretical_learning": "theoretical_learning",
}


def normalize_rule_scores(scores: dict[str, float]) -> dict[str, float]:
    return {key: max(0.0, min(float(value), 1.0)) for key, value in scores.items()}


def compute_confidence(
    completeness: float, top_score: float, second_score: float, abstentions: list[str], evidence_count: int
) -> ConfidenceLevel:
    if completeness < 0.55 or "RULE_ABSTAIN_INCOMPLETE" in abstentions:
        return ConfidenceLevel.insufficient
    separation = top_score - second_score
    if separation < 0.05 or "RULE_ABSTAIN_MULTI_AFFINITY" in abstentions:
        return ConfidenceLevel.low
    if evidence_count >= 5 and completeness >= 0.9 and separation >= 0.15:
        return ConfidenceLevel.high
    return ConfidenceLevel.medium


async def build_feature_profile(db: AsyncSession, attempt: AssessmentAttempt) -> dict[str, Any]:
    answers = (
        await db.execute(select(AssessmentAnswer).where(AssessmentAnswer.attempt_id == attempt.id))
    ).scalars().all()
    features: dict[str, Any] = {}
    for answer in answers:
        feature_key = QUESTION_FEATURE_MAP.get(answer.question_key, answer.question_key)
        features[feature_key] = answer.value
    return features


async def generate_recommendations(
    db: AsyncSession, attempt: AssessmentAttempt
) -> dict[str, Any]:
    features = await build_feature_profile(db, attempt)
    programs = (await db.execute(select(AcademicProgram))).scalars().all()
    expert_scores_raw, triggered_rules, abstentions = score_rules(features)
    ml_scores_raw, model_version, model_metadata = score_ml(features)
    graph_scores_raw, graph_paths = score_graph(features)
    expert_scores = normalize_rule_scores(expert_scores_raw)
    ml_scores = {key: max(0.0, min(float(value), 1.0)) for key, value in ml_scores_raw.items()}
    graph_scores = {key: max(0.0, min(float(value), 1.0)) for key, value in graph_scores_raw.items()}

    combined: dict[str, float] = defaultdict(float)
    for program in programs:
        slug = program.slug
        combined[slug] += expert_scores.get(slug, 0.0) * settings.experimental_expert_weight
        combined[slug] += ml_scores.get(slug, 0.0) * settings.experimental_ml_weight
        combined[slug] += graph_scores.get(slug, 0.0) * settings.experimental_graph_weight
    ranked = sorted(combined.items(), key=lambda item: item[1], reverse=True)
    top_score = ranked[0][1] if ranked else 0.0
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    completeness = attempt.progress / 100
    confidence = compute_confidence(completeness, top_score, second_score, abstentions, len(triggered_rules))
    top_items = []
    for index, (slug, score) in enumerate(ranked[:5], start=1):
        top_items.append(
            {
                "program_slug": slug,
                "rank": index,
                "compatibility_score": round(float(score) * 100, 2),
                "confidence_level": confidence.value,
                "triggered_rules": [rule for rule in triggered_rules if any(action["target"] == slug for action in rule["actions"])],
                "supporting_factors": [
                    f"Coincidencia entre intereses y habilidades reportadas para {slug.replace('-', ' ')}.",
                    "El sistema encontro evidencia en reglas y perfil estructurado.",
                ],
                "development_factors": [
                    "Confirma tus preferencias de entorno laboral para mejorar la precision.",
                    "Explora asignaturas introductorias del area para validar interes sostenido.",
                ],
                "knowledge_graph_paths": graph_paths.get(slug, []),
            }
        )
    top_compatibility = cast(float, top_items[0]["compatibility_score"]) if top_items else 0.0
    return {
        "compatibility_score": round(top_compatibility, 2),
        "confidence_level": confidence.value,
        "score_components": {
            "expert_weight": settings.experimental_expert_weight,
            "ml_weight": settings.experimental_ml_weight,
            "graph_weight": settings.experimental_graph_weight,
            "expert_scores": expert_scores,
            "ml_scores": ml_scores,
            "graph_scores": graph_scores,
            "abstentions": abstentions,
            "model_metadata": model_metadata,
        },
        "structured_explanation": {
            "profile_summary": "Orientacion exploratoria basada en respuestas estructuradas y datos de demostracion.",
            "evidence_count": len(triggered_rules),
            "requested_more_information": confidence in {ConfidenceLevel.low, ConfidenceLevel.insufficient},
        },
        "model_version": model_version,
        "rule_version": "ruleset-v1",
        "explanation_version": "exp-v1",
        "recommendations": top_items,
    }
