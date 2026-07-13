from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RecommendationItemResponse(BaseModel):
    id: str
    program_slug: str
    rank: int
    compatibility_score: float
    confidence_level: str
    triggered_rules: list[dict[str, Any]]
    supporting_factors: list[str]
    development_factors: list[str]
    knowledge_graph_paths: list[dict[str, Any]]


class RecommendationRunResponse(BaseModel):
    id: str
    compatibility_score: float
    confidence_level: str
    score_components: dict[str, Any]
    structured_explanation: dict[str, Any]
    model_version: str
    explanation_version: str
    recommendations: list[RecommendationItemResponse]


class FeedbackRequest(BaseModel):
    helpful: bool
    comment: str | None = Field(default=None, max_length=1000)
