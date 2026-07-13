from __future__ import annotations

from math import ceil
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AssessmentAnswer,
    AssessmentAttempt,
    AssessmentDefinition,
    AssessmentOption,
    AssessmentQuestion,
    AssessmentSection,
)


async def get_current_assessment(db: AsyncSession) -> dict[str, Any]:
    definition = (
        await db.execute(select(AssessmentDefinition).where(AssessmentDefinition.slug == "orientaia-main"))
    ).scalar_one()
    sections = (
        await db.execute(
            select(AssessmentSection).where(AssessmentSection.definition_id == definition.id).order_by(AssessmentSection.order_index)
        )
    ).scalars().all()
    questions = (await db.execute(select(AssessmentQuestion).order_by(AssessmentQuestion.order_index))).scalars().all()
    options = (await db.execute(select(AssessmentOption).order_by(AssessmentOption.order_index))).scalars().all()
    question_map: dict[str, list[dict[str, Any]]] = {}
    for option in options:
        question_map.setdefault(str(option.question_id), []).append({"label": option.label, "value": option.value})
    section_questions: dict[str, list[dict[str, Any]]] = {}
    for question in questions:
        section_questions.setdefault(str(question.section_id), []).append(
            {
                "key": question.key,
                "prompt": question.prompt,
                "help_text": question.help_text,
                "question_type": question.question_type,
                "required": question.required,
                "config": question.config,
                "options": question_map.get(str(question.id), []),
            }
        )
    return {
        "slug": definition.slug,
        "title": definition.title,
        "description": definition.description,
        "version": definition.current_version,
        "sections": [
            {
                "key": section.key,
                "title": section.title,
                "description": section.description,
                "questions": section_questions.get(str(section.id), []),
            }
            for section in sections
        ],
    }


async def serialize_attempt(db: AsyncSession, attempt: AssessmentAttempt) -> dict[str, Any]:
    answers = (
        await db.execute(select(AssessmentAnswer).where(AssessmentAnswer.attempt_id == attempt.id))
    ).scalars().all()
    return {
        "id": str(attempt.id),
        "version": attempt.version,
        "status": attempt.status.value,
        "progress": attempt.progress,
        "estimated_minutes_remaining": attempt.estimated_minutes_remaining,
        "answers": {answer.question_key: answer.value for answer in answers},
    }


async def update_attempt_answers(
    db: AsyncSession, attempt: AssessmentAttempt, answers: dict[str, Any]
) -> AssessmentAttempt:
    for key, value in answers.items():
        existing = (
            await db.execute(
                select(AssessmentAnswer).where(
                    AssessmentAnswer.attempt_id == attempt.id, AssessmentAnswer.question_key == key
                )
            )
        ).scalar_one_or_none()
        if existing:
            existing.value = value
        else:
            db.add(AssessmentAnswer(attempt_id=attempt.id, question_key=key, value=value))

    total_questions = (await db.execute(select(AssessmentQuestion))).scalars().all()
    total_count = len(total_questions)
    saved_count = len(
        (await db.execute(select(AssessmentAnswer).where(AssessmentAnswer.attempt_id == attempt.id))).scalars().all()
    ) + len([key for key in answers if key])
    completion_ratio = min(saved_count / total_count, 1.0) if total_count else 0.0
    attempt.progress = round(completion_ratio * 100, 2)
    attempt.estimated_minutes_remaining = max(2, ceil((1 - completion_ratio) * 15))
    await db.commit()
    await db.refresh(attempt)
    return attempt
