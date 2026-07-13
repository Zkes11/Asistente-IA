from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, SoftDeleteMixin, TimestampMixin


class RoleName(str, enum.Enum):
    student = "student"
    counselor = "counselor"
    admin = "admin"


class AttemptStatus(str, enum.Enum):
    draft = "draft"
    completed = "completed"


class ConfidenceLevel(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"
    insufficient = "insufficient"


class ActionStepStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    postponed = "postponed"


class User(Base, IdMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    preferred_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    profile: Mapped[UserProfile] = relationship(back_populates="user", uselist=False)
    roles: Mapped[list[UserRole]] = relationship(back_populates="user")


class Role(Base, IdMixin, TimestampMixin):
    __tablename__ = "roles"

    name: Mapped[RoleName] = mapped_column(Enum(RoleName), unique=True)


class UserRole(Base, IdMixin, TimestampMixin):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))

    user: Mapped[User] = relationship(back_populates="roles")
    role: Mapped[Role] = relationship()


class UserProfile(Base, IdMixin, TimestampMixin):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    grade_level: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    goal: Mapped[str | None] = mapped_column(String(120), nullable=True)
    known_areas: Mapped[list[str]] = mapped_column(JSON, default=list)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    privacy_policy_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    assessment_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    guardian_consent_required: Mapped[bool] = mapped_column(Boolean, default=False)
    guardian_consent_granted: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship(back_populates="profile")


class Consent(Base, IdMixin, TimestampMixin):
    __tablename__ = "consents"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    consent_type: Mapped[str] = mapped_column(String(120))
    version: Mapped[str] = mapped_column(String(40))
    accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RefreshToken(Base, IdMixin, TimestampMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AssessmentDefinition(Base, IdMixin, TimestampMixin):
    __tablename__ = "assessment_definitions"

    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    current_version: Mapped[str] = mapped_column(String(40))


class AssessmentSection(Base, IdMixin, TimestampMixin):
    __tablename__ = "assessment_sections"

    definition_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assessment_definitions.id", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer)


class AssessmentQuestion(Base, IdMixin, TimestampMixin):
    __tablename__ = "assessment_questions"

    section_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assessment_sections.id", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    prompt: Mapped[str] = mapped_column(Text)
    help_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    question_type: Mapped[str] = mapped_column(String(40))
    order_index: Mapped[int] = mapped_column(Integer)
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class AssessmentOption(Base, IdMixin, TimestampMixin):
    __tablename__ = "assessment_options"

    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assessment_questions.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String(255))
    value: Mapped[str] = mapped_column(String(120))
    weight_map: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)
    order_index: Mapped[int] = mapped_column(Integer)


class AssessmentVersion(Base, IdMixin, TimestampMixin):
    __tablename__ = "assessment_versions"

    definition_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assessment_definitions.id", ondelete="CASCADE"))
    version: Mapped[str] = mapped_column(String(40), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    schema_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class AssessmentAttempt(Base, IdMixin, TimestampMixin):
    __tablename__ = "assessment_attempts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    definition_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assessment_definitions.id"))
    version: Mapped[str] = mapped_column(String(40))
    status: Mapped[AttemptStatus] = mapped_column(Enum(AttemptStatus), default=AttemptStatus.draft)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_minutes_remaining: Mapped[int] = mapped_column(Integer, default=15)
    answers: Mapped[list[AssessmentAnswer]] = relationship(back_populates="attempt")


class AssessmentAnswer(Base, IdMixin, TimestampMixin):
    __tablename__ = "assessment_answers"
    __table_args__ = (UniqueConstraint("attempt_id", "question_key", name="uq_attempt_question"),)

    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assessment_attempts.id", ondelete="CASCADE"))
    question_key: Mapped[str] = mapped_column(String(120), index=True)
    value: Mapped[Any] = mapped_column(JSON)

    attempt: Mapped[AssessmentAttempt] = relationship(back_populates="answers")


class AcademicArea(Base, IdMixin, TimestampMixin):
    __tablename__ = "academic_areas"

    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)


class AcademicProgram(Base, IdMixin, TimestampMixin):
    __tablename__ = "academic_programs"

    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    short_description: Mapped[str] = mapped_column(Text)
    academic_area_slug: Mapped[str] = mapped_column(String(120), index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    source_name: Mapped[str] = mapped_column(String(255), default="Datos de demostracion")
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_reference_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class University(Base, IdMixin, TimestampMixin):
    __tablename__ = "universities"

    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=True)
    source_name: Mapped[str] = mapped_column(String(255), default="Datos de demostracion")
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ExpertRule(Base, IdMixin, TimestampMixin):
    __tablename__ = "expert_rules"

    rule_key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    current_version: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class RuleVersion(Base, IdMixin, TimestampMixin):
    __tablename__ = "rule_versions"

    rule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("expert_rules.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer)
    definition: Mapped[dict[str, Any]] = mapped_column(JSON)


class ModelVersion(Base, IdMixin, TimestampMixin):
    __tablename__ = "model_versions"

    version: Mapped[str] = mapped_column(String(80), unique=True)
    status: Mapped[str] = mapped_column(String(40), default="candidate")
    artifact_path: Mapped[str] = mapped_column(String(500))
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RecommendationRun(Base, IdMixin, TimestampMixin):
    __tablename__ = "recommendation_runs"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    assessment_attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assessment_attempts.id"))
    rule_version: Mapped[str] = mapped_column(String(80))
    model_version: Mapped[str] = mapped_column(String(80))
    assessment_version: Mapped[str] = mapped_column(String(80))
    explanation_version: Mapped[str] = mapped_column(String(80))
    confidence_level: Mapped[ConfidenceLevel] = mapped_column(Enum(ConfidenceLevel))
    compatibility_score: Mapped[float] = mapped_column(Float)
    score_components: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    structured_explanation: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class Recommendation(Base, IdMixin, TimestampMixin):
    __tablename__ = "recommendations"

    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recommendation_runs.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    program_slug: Mapped[str] = mapped_column(String(120), index=True)
    rank: Mapped[int] = mapped_column(Integer)
    compatibility_score: Mapped[float] = mapped_column(Float)
    confidence_level: Mapped[ConfidenceLevel] = mapped_column(Enum(ConfidenceLevel))
    triggered_rules: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    supporting_factors: Mapped[list[str]] = mapped_column(JSON, default=list)
    development_factors: Mapped[list[str]] = mapped_column(JSON, default=list)
    knowledge_graph_paths: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)


class RecommendationFeedback(Base, IdMixin, TimestampMixin):
    __tablename__ = "recommendation_feedback"

    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("recommendations.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    helpful: Mapped[bool] = mapped_column(Boolean)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)


class FavoriteProgram(Base, IdMixin, TimestampMixin):
    __tablename__ = "favorite_programs"
    __table_args__ = (UniqueConstraint("user_id", "program_slug", name="uq_favorite_program"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    program_slug: Mapped[str] = mapped_column(String(120), index=True)


class ActionPlan(Base, IdMixin, TimestampMixin):
    __tablename__ = "action_plans"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    recommendation_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("recommendation_runs.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)


class ActionPlanStep(Base, IdMixin, TimestampMixin):
    __tablename__ = "action_plan_steps"

    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("action_plans.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(40), default="medium")
    status: Mapped[ActionStepStatus] = mapped_column(Enum(ActionStepStatus), default=ActionStepStatus.pending)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resources: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)


class ChatSession(Base, IdMixin, TimestampMixin):
    __tablename__ = "chat_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    external_llm_enabled: Mapped[bool] = mapped_column(Boolean, default=False)


class ChatMessage(Base, IdMixin, TimestampMixin):
    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(40))
    content: Mapped[str] = mapped_column(Text)
    citations: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)


class DataExport(Base, IdMixin, TimestampMixin):
    __tablename__ = "data_exports"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(40), default="completed")
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class DeletionRequest(Base, IdMixin, TimestampMixin):
    __tablename__ = "deletion_requests"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(40), default="requested")
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base, IdMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(), nullable=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str] = mapped_column(String(120))
    entity_id: Mapped[str] = mapped_column(String(120))
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
