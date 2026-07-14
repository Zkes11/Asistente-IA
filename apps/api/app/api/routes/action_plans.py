from __future__ import annotations

import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models import ActionPlan, ActionPlanStep, ChatMessage, ChatSession, Recommendation, RecommendationRun, User
from app.db.session import get_db
from app.schemas.action_plans import (
    ActionPlanResponse,
    ActionPlanStepResponse,
    CreateActionPlanRequest,
    UpdateActionPlanStepRequest,
)
from app.schemas.common import MessageResponse
from app.services.chat_provider import generate_action_plan_content

router = APIRouter()

CHAT_AREA_HINTS = {
    "tecnologia": {
        "keywords": ["tecnologia", "software", "programar", "codigo", "apps", "sistemas", "digital", "computador"],
        "study": "fundamentos digitales, logica, programacion inicial y resolucion de problemas",
        "practice": "un mini proyecto, automatizacion simple o ejercicios guiados",
    },
    "datos": {
        "keywords": ["datos", "analisis", "estadistica", "metricas", "tablas", "numeros", "patrones"],
        "study": "lectura de datos, estadistica basica y pensamiento analitico",
        "practice": "tablas, visualizaciones sencillas o retos de interpretacion",
    },
    "diseno": {
        "keywords": ["diseno", "visual", "creativo", "interfaces", "dibujar", "colores", "ux", "grafico"],
        "study": "composicion visual, experiencia de usuario y comunicacion grafica",
        "practice": "bocetos, redisenos o tableros visuales",
    },
    "social": {
        "keywords": ["ayudar", "personas", "social", "acompanar", "comunidad", "escuchar", "orientar"],
        "study": "escucha activa, observacion social y analisis de contextos humanos",
        "practice": "voluntariado, entrevistas o ejercicios de acompanamiento",
    },
    "salud": {
        "keywords": ["salud", "cuidado", "bienestar", "pacientes", "clinico", "medico", "enfermeria", "biologia", "quimica", "laboratorio"],
        "study": "bases de cuidado, bienestar y ciencias de la salud",
        "practice": "simulaciones, habitos de cuidado y exploracion de roles asistenciales",
    },
    "negocios": {
        "keywords": ["negocio", "empresa", "liderar", "ventas", "emprender", "estrategia", "administracion"],
        "study": "gestion, estrategia, organizacion y toma de decisiones",
        "practice": "casos de negocio, presupuestos basicos o ideas de emprendimiento",
    },
}


def humanize_program_slug(slug: str) -> str:
    return slug.replace("-", " ").title()


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def sentence_excerpt(value: str, limit: int = 140) -> str:
    cleaned = compact_text(value)
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 3].rstrip()}..."


def area_signal_score(text: str, keywords: list[str]) -> int:
    positive_hits = sum(1 for keyword in keywords if keyword in text)
    negative_hits = sum(
        1
        for keyword in keywords
        if re.search(rf"(?:no|casi no|nada|poco|evito|me aburre)[\s\S]{{0,18}}{re.escape(keyword)}", text)
    )
    return positive_hits - (negative_hits * 2)


def summarize_chat_messages(messages: list[ChatMessage]) -> dict[str, object]:
    user_messages = [message for message in messages if message.role == "user"]
    assistant_messages = [message for message in messages if message.role == "assistant"]
    user_excerpts = [sentence_excerpt(message.content) for message in user_messages if compact_text(message.content)]
    assistant_prompts = [
        sentence_excerpt(message.content)
        for message in assistant_messages
        if "?" in message.content or "cuent" in message.content.lower() or "habla" in message.content.lower()
    ]

    joined_user_text = compact_text(" ".join(message.content.lower() for message in user_messages))
    ranked_areas: list[tuple[str, int]] = []
    for area, config in CHAT_AREA_HINTS.items():
        signal_score = area_signal_score(joined_user_text, config["keywords"])
        if signal_score > 0:
            ranked_areas.append((area, signal_score))
    ranked_areas.sort(key=lambda item: item[1], reverse=True)

    focus_areas = [area for area, _ in ranked_areas[:2]]
    study_focus = [CHAT_AREA_HINTS[area]["study"] for area in focus_areas]
    practice_focus = [CHAT_AREA_HINTS[area]["practice"] for area in focus_areas]

    return {
        "user_excerpts": user_excerpts[:3],
        "assistant_prompts": assistant_prompts[-3:],
        "focus_areas": focus_areas,
        "study_focus": study_focus,
        "practice_focus": practice_focus,
    }


def serialize_step(step: ActionPlanStep) -> ActionPlanStepResponse:
    return ActionPlanStepResponse(
        id=str(step.id),
        title=step.title,
        description=step.description,
        priority=step.priority,
        status=step.status.value,
        progress=step.progress,
        notes=step.notes,
        resources=step.resources,
        due_date=step.due_date.isoformat() if step.due_date else None,
    )


async def serialize_plan(db: AsyncSession, plan: ActionPlan) -> ActionPlanResponse:
    steps = (
        await db.execute(select(ActionPlanStep).where(ActionPlanStep.plan_id == plan.id))
    ).scalars().all()
    return ActionPlanResponse(
        id=str(plan.id),
        title=plan.title,
        summary=plan.summary,
        created_at=plan.created_at.isoformat(),
        steps=[serialize_step(step) for step in steps],
    )


@router.get("", response_model=list[ActionPlanResponse])
async def list_plans(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[ActionPlanResponse]:
    plans = (
        await db.execute(
            select(ActionPlan).where(ActionPlan.user_id == current_user.id).order_by(ActionPlan.created_at.desc())
        )
    ).scalars().all()
    return [await serialize_plan(db, plan) for plan in plans]


@router.get("/current", response_model=ActionPlanResponse | None)
async def current_plan(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ActionPlanResponse | None:
    plan = (
        await db.execute(
            select(ActionPlan).where(ActionPlan.user_id == current_user.id).order_by(ActionPlan.created_at.desc())
        )
    ).scalars().first()
    return await serialize_plan(db, plan) if plan else None


@router.get("/{plan_id}", response_model=ActionPlanResponse)
async def get_plan(
    plan_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ActionPlanResponse:
    plan = (
        await db.execute(
            select(ActionPlan).where(ActionPlan.id == uuid.UUID(plan_id), ActionPlan.user_id == current_user.id)
        )
    ).scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan no encontrado")
    return await serialize_plan(db, plan)


@router.post("", response_model=ActionPlanResponse)
async def create_plan(
    payload: CreateActionPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ActionPlanResponse:
    existing_plan_count = len(
        (
            await db.execute(select(ActionPlan).where(ActionPlan.user_id == current_user.id))
        ).scalars().all()
    )
    chat_label = f"Chat #{existing_plan_count + 1}"
    chat_context: dict[str, object] = {
        "user_excerpts": [],
        "assistant_prompts": [],
        "focus_areas": [],
        "study_focus": [],
        "practice_focus": [],
    }
    if payload.chat_session_id:
        chat_session = (
            await db.execute(
                select(ChatSession).where(
                    ChatSession.id == uuid.UUID(payload.chat_session_id), ChatSession.user_id == current_user.id
                )
            )
        ).scalar_one_or_none()
        if chat_session:
            chat_label = chat_session.title
            chat_messages = (
                await db.execute(
                    select(ChatMessage)
                    .where(ChatMessage.session_id == chat_session.id)
                    .order_by(ChatMessage.created_at)
                )
            ).scalars().all()
            chat_context = summarize_chat_messages(chat_messages)

    plan_title = f"Plan de {chat_label}"
    focus_areas = chat_context["focus_areas"]
    user_excerpts = chat_context["user_excerpts"]
    assistant_prompts = chat_context["assistant_prompts"]
    study_focus = chat_context["study_focus"]
    practice_focus = chat_context["practice_focus"]

    if user_excerpts:
        excerpts_text = " | ".join(f'"{excerpt}"' for excerpt in user_excerpts[:2])
        plan_summary = f"Basado en tu conversacion {chat_label.lower()}, detecte estas senales: {excerpts_text}."
    else:
        plan_summary = "Ruta editable basada en tu conversacion y recomendaciones actuales."
    step_blueprint = [
        ("Explorar programas", "Revisa planes de estudio y campos de accion.", "high"),
        ("Comparar opciones", "Compara al menos tres programas cercanos.", "high"),
        ("Fortalecer habilidades", "Selecciona una habilidad clave para practicar.", "medium"),
        ("Hablar con un orientador", "Solicita acompanamiento humano para validar hallazgos.", "medium"),
    ]

    if payload.recommendation_run_id:
        run = (
            await db.execute(
                select(RecommendationRun).where(
                    RecommendationRun.id == uuid.UUID(payload.recommendation_run_id),
                    RecommendationRun.user_id == current_user.id,
                )
            )
        ).scalar_one_or_none()
        top_recommendations = []
        if run:
            top_recommendations = (
                await db.execute(
                    select(Recommendation)
                    .where(Recommendation.run_id == run.id)
                    .order_by(Recommendation.rank)
                )
            ).scalars().all()
        recommendation_payload = [
            {
                "program_name": humanize_program_slug(item.program_slug),
                "supporting_factors": item.supporting_factors,
                "development_factors": item.development_factors,
            }
            for item in top_recommendations[:2]
        ]
        provider_plan = generate_action_plan_content(chat_label, chat_context, recommendation_payload)
        plan_title = provider_plan["title"]
        plan_summary = provider_plan["summary"]
        step_blueprint = [
            (step["title"], step["description"], step["priority"])
            for step in provider_plan["steps"]
        ]

    plan = ActionPlan(
        user_id=current_user.id,
        recommendation_run_id=uuid.UUID(payload.recommendation_run_id) if payload.recommendation_run_id else None,
        title=plan_title,
        summary=plan_summary,
    )
    db.add(plan)
    await db.flush()
    for title, description, priority in step_blueprint:
        db.add(
            ActionPlanStep(
                plan_id=plan.id,
                title=title,
                description=description,
                priority=priority,
                resources=[
                    {"label": "Ruta de estudio sugerida", "url": "#"},
                    {"label": "Consejo vocacional", "url": "#"},
                ],
            )
        )
    await db.commit()
    await db.refresh(plan)
    return await serialize_plan(db, plan)


@router.patch("/{plan_id}", response_model=ActionPlanResponse)
async def patch_plan(
    plan_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ActionPlanResponse:
    plan = (
        await db.execute(
            select(ActionPlan).where(ActionPlan.id == uuid.UUID(plan_id), ActionPlan.user_id == current_user.id)
        )
    ).scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan no encontrado")
    return await serialize_plan(db, plan)


@router.patch("/{plan_id}/steps/{step_id}", response_model=ActionPlanStepResponse)
async def patch_plan_step(
    plan_id: str,
    step_id: str,
    payload: UpdateActionPlanStepRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ActionPlanStepResponse:
    plan = (
        await db.execute(
            select(ActionPlan).where(ActionPlan.id == uuid.UUID(plan_id), ActionPlan.user_id == current_user.id)
        )
    ).scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan no encontrado")
    step = (
        await db.execute(
            select(ActionPlanStep).where(ActionPlanStep.id == uuid.UUID(step_id), ActionPlanStep.plan_id == plan.id)
        )
    ).scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paso no encontrado")
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(step, field, value)
    await db.commit()
    await db.refresh(step)
    return serialize_step(step)
