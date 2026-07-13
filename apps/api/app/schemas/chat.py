from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatSessionResponse(BaseModel):
    id: str
    title: str
    external_llm_enabled: bool


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    citations: list[dict[str, str]]
    created_at: str


class CreateChatSessionRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    external_llm_enabled: bool = False


class SendChatMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class AppendChatMessageRequest(BaseModel):
    role: Literal["assistant", "user"] = "assistant"
    content: str = Field(min_length=1, max_length=4000)
    citations: list[dict[str, str]] = Field(default_factory=list)


class InterviewTurnRequest(BaseModel):
    answers: dict[str, int | str | float] = Field(default_factory=dict)
    max_follow_up_questions: int = Field(default=4, ge=1, le=8)
    mode: Literal["start", "advance"] = "advance"
    evaluated_feature_key: str | None = None
    evaluated_feature_score: float | None = None


class InterviewTurnResponse(BaseModel):
    messages: list[str]
    feature_key: str | None = None
    should_finalize: bool = False
    rationale: str | None = None
    answer_updates: dict[str, float] = Field(default_factory=dict)
    merged_answers: dict[str, float] = Field(default_factory=dict)
