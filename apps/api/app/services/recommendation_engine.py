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


def compute_dynamic_weights(
    feature_count: int,
    abstentions: list[str],
) -> tuple[float, float, float]:
    expert_weight = settings.experimental_expert_weight
    ml_weight = settings.experimental_ml_weight
    graph_weight = settings.experimental_graph_weight

    if feature_count < 8 or "RULE_ABSTAIN_INCOMPLETE" in abstentions:
        expert_weight *= 1.25
        ml_weight *= 0.18
        graph_weight *= 1.25

    total = expert_weight + ml_weight + graph_weight
    if total <= 0:
        return (0.3, 0.4, 0.3)
    return (expert_weight / total, ml_weight / total, graph_weight / total)


def apply_domain_adjustments(features: dict[str, Any], combined: dict[str, float]) -> dict[str, float]:
    adjusted = dict(combined)

    interest_health = float(features.get("interest_health", 0) or 0)
    interest_social = float(features.get("interest_social", 0) or 0)
    practical_learning = float(features.get("practical_learning", 0) or 0)
    interest_technology = float(features.get("interest_technology", 0) or 0)
    numerical_skill = float(features.get("numerical_skill", 0) or 0)
    empathy = float(features.get("empathy", 0) or 0)
    communication = float(features.get("communication", 0) or 0)
    teamwork_preference = float(features.get("teamwork_preference", 0) or 0)
    autonomy_preference = float(features.get("autonomy_preference", 0) or 0)

    if interest_health >= 4 and practical_learning >= 4 and interest_technology <= 2:
        for slug in ["ingenieria-de-sistemas", "ingenieria-de-software", "ciberseguridad", "ciencia-de-datos"]:
            adjusted[slug] = adjusted.get(slug, 0.0) * 0.15
        adjusted["fisioterapia"] = adjusted.get("fisioterapia", 0.0) + 0.20
        adjusted["enfermeria"] = adjusted.get("enfermeria", 0.0) + 0.12
        adjusted["educacion"] = adjusted.get("educacion", 0.0) + 0.08

    if interest_health <= 2:
        for slug in ["enfermeria", "fisioterapia", "biologia", "quimica-aplicada"]:
            adjusted[slug] = adjusted.get(slug, 0.0) * 0.25

    if numerical_skill <= 2:
        for slug in ["ciencia-de-datos", "analitica-de-negocios", "finanzas", "ingenieria-de-sistemas"]:
            adjusted[slug] = adjusted.get(slug, 0.0) * 0.55

    if empathy <= 2 and communication <= 2:
        for slug in ["trabajo-social", "psicologia"]:
            adjusted[slug] = adjusted.get(slug, 0.0) * 0.40

    if practical_learning >= 4 and teamwork_preference >= 4 and interest_health <= 2:
        adjusted["educacion"] = adjusted.get("educacion", 0.0) + 0.18
        adjusted["administracion-de-empresas"] = adjusted.get("administracion-de-empresas", 0.0) + 0.08
        adjusted["marketing-digital"] = adjusted.get("marketing-digital", 0.0) + 0.05

    if autonomy_preference >= 4 and practical_learning >= 4 and interest_technology <= 2 and numerical_skill <= 2:
        for slug in ["ingenieria-de-sistemas", "ingenieria-de-software", "ciencia-de-datos"]:
            adjusted[slug] = adjusted.get(slug, 0.0) * 0.35

    if interest_social <= 2 and empathy <= 2:
        for slug in ["trabajo-social", "psicologia", "enfermeria"]:
            adjusted[slug] = adjusted.get(slug, 0.0) * 0.40

    return adjusted


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
    feature_count = sum(1 for value in features.values() if value not in (None, "", 0, "0"))
    expert_weight, ml_weight, graph_weight = compute_dynamic_weights(feature_count, abstentions)

    combined: dict[str, float] = defaultdict(float)
    for program in programs:
        slug = program.slug
        combined[slug] += expert_scores.get(slug, 0.0) * expert_weight
        combined[slug] += ml_scores.get(slug, 0.0) * ml_weight
        combined[slug] += graph_scores.get(slug, 0.0) * graph_weight
    combined = defaultdict(float, apply_domain_adjustments(features, combined))
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
            "expert_weight": expert_weight,
            "ml_weight": ml_weight,
            "graph_weight": graph_weight,
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
