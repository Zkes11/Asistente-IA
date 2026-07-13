from __future__ import annotations

from pydantic import BaseModel, Field


class ActionPlanStepResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    status: str
    progress: int
    notes: str | None
    resources: list[dict[str, str]]
    due_date: str | None


class ActionPlanResponse(BaseModel):
    id: str
    title: str
    summary: str
    created_at: str
    steps: list[ActionPlanStepResponse]


class CreateActionPlanRequest(BaseModel):
    recommendation_run_id: str | None = None
    chat_session_id: str | None = None


class UpdateActionPlanStepRequest(BaseModel):
    status: str | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    notes: str | None = None
