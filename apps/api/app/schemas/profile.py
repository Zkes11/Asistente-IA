from __future__ import annotations

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    preferred_name: str | None
    grade_level: str | None
    country: str | None
    city: str | None
    goal: str | None
    known_areas: list[str]
    onboarding_completed: bool
    privacy_policy_accepted: bool
    assessment_consent: bool
    guardian_consent_required: bool
    guardian_consent_granted: bool


class ProfileUpdateRequest(BaseModel):
    preferred_name: str | None = Field(default=None, max_length=120)
    grade_level: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=120)
    city: str | None = Field(default=None, max_length=120)
    goal: str | None = Field(default=None, max_length=120)
    known_areas: list[str] = Field(default_factory=list)
    onboarding_completed: bool | None = None
    privacy_policy_accepted: bool | None = None
    assessment_consent: bool | None = None
    guardian_consent_required: bool | None = None
    guardian_consent_granted: bool | None = None
