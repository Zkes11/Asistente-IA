from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AssessmentOptionResponse(BaseModel):
    label: str
    value: str


class AssessmentQuestionResponse(BaseModel):
    key: str
    prompt: str
    help_text: str | None
    question_type: str
    required: bool
    config: dict[str, Any]
    options: list[AssessmentOptionResponse]


class AssessmentSectionResponse(BaseModel):
    key: str
    title: str
    description: str
    questions: list[AssessmentQuestionResponse]


class CurrentAssessmentResponse(BaseModel):
    slug: str
    title: str
    description: str
    version: str
    sections: list[AssessmentSectionResponse]


class AssessmentAttemptResponse(BaseModel):
    id: str
    version: str
    status: str
    progress: float
    estimated_minutes_remaining: int
    answers: dict[str, Any]


class CreateAttemptRequest(BaseModel):
    definition_slug: str = "orientaia-main"


class PatchAnswersRequest(BaseModel):
    answers: dict[str, Any]
