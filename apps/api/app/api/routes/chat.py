from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models import (
    ActionPlan,
    ActionPlanStep,
    ChatMessage,
    ChatSession,
    Recommendation,
    RecommendationRun,
    User,
)
from app.db.session import get_db
from app.schemas.chat import (
    AppendChatMessageRequest,
    ChatMessageResponse,
    ChatSessionResponse,
    CreateChatSessionRequest,
    InterviewTurnRequest,
    InterviewTurnResponse,
    SendChatMessageRequest,
)
from app.schemas.common import MessageResponse
from app.services.chat_provider import deterministic_reply, generate_interview_assistant_turn

router = APIRouter()


def serialize_message(message: ChatMessage) -> ChatMessageResponse:
    return ChatMessageResponse(
        id=str(message.id),
        role=message.role,
        content=message.content,
        citations=message.citations,
        created_at=message.created_at.isoformat(),
    )


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    payload: CreateChatSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatSessionResponse:
    session = ChatSession(
        user_id=current_user.id, title=payload.title, external_llm_enabled=payload.external_llm_enabled
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return ChatSessionResponse(id=str(session.id), title=session.title, external_llm_enabled=session.external_llm_enabled)


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[ChatSessionResponse]:
    sessions = (
        await db.execute(
            select(ChatSession).where(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc())
        )
    ).scalars().all()
    return [
        ChatSessionResponse(id=str(session.id), title=session.title, external_llm_enabled=session.external_llm_enabled)
        for session in sessions
    ]


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def delete_session(
    session_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    session = (
        await db.execute(
            select(ChatSession).where(ChatSession.id == uuid.UUID(session_id), ChatSession.user_id == current_user.id)
        )
    ).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesion no encontrada")
    # Delete messages first to avoid FK constraint
    messages = (
        await db.execute(select(ChatMessage).where(ChatMessage.session_id == session.id))
    ).scalars().all()
    for message in messages:
        await db.delete(message)
    await db.delete(session)
    await db.commit()
    return MessageResponse(message="Sesion eliminada")


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def list_messages(
    session_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[ChatMessageResponse]:
    session = (
        await db.execute(
            select(ChatSession).where(ChatSession.id == uuid.UUID(session_id), ChatSession.user_id == current_user.id)
        )
    ).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesion no encontrada")
    messages = (
        await db.execute(select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at))
    ).scalars().all()
    return [serialize_message(message) for message in messages]


@router.post("/sessions/{session_id}/messages/raw", response_model=ChatMessageResponse)
async def append_message(
    session_id: str,
    payload: AppendChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    session = (
        await db.execute(
            select(ChatSession).where(ChatSession.id == uuid.UUID(session_id), ChatSession.user_id == current_user.id)
        )
    ).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesion no encontrada")
    message = ChatMessage(
        session_id=session.id,
        user_id=current_user.id,
        role=payload.role,
        content=payload.content,
        citations=payload.citations,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return serialize_message(message)


@router.post("/sessions/{session_id}/interview-turn", response_model=InterviewTurnResponse)
async def create_interview_turn(
    session_id: str,
    payload: InterviewTurnRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterviewTurnResponse:
    session = (
        await db.execute(
            select(ChatSession).where(ChatSession.id == uuid.UUID(session_id), ChatSession.user_id == current_user.id)
        )
    ).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesion no encontrada")
    messages = (
        await db.execute(select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at))
    ).scalars().all()
    user_messages = [message.content for message in messages if message.role == "user"]
    turn = generate_interview_assistant_turn(
        payload.answers,
        user_messages,
        payload.max_follow_up_questions,
        payload.mode,
        payload.evaluated_feature_key,
        payload.evaluated_feature_score,
    )
    return InterviewTurnResponse(**turn)


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    session_id: str,
    payload: SendChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    session = (
        await db.execute(
            select(ChatSession).where(ChatSession.id == uuid.UUID(session_id), ChatSession.user_id == current_user.id)
        )
    ).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesion no encontrada")
    user_message = ChatMessage(session_id=session.id, user_id=current_user.id, role="user", content=payload.content)
    db.add(user_message)
    run = (
        await db.execute(
            select(RecommendationRun)
            .where(RecommendationRun.user_id == current_user.id)
            .order_by(RecommendationRun.created_at.desc())
        )
    ).scalars().first()
    recommendations: list[dict[str, object]] = []
    if run:
        items = (
            await db.execute(select(Recommendation).where(Recommendation.run_id == run.id).order_by(Recommendation.rank))
        ).scalars().all()
        recommendations = [
            {"id": str(item.id), "program_slug": item.program_slug, "compatibility_score": item.compatibility_score}
            for item in items
        ]
    plan = (
        await db.execute(select(ActionPlan).where(ActionPlan.user_id == current_user.id).order_by(ActionPlan.created_at.desc()))
    ).scalars().first()
    serialized_plan = None
    if plan:
        steps = (
            await db.execute(select(ActionPlanStep).where(ActionPlanStep.plan_id == plan.id))
        ).scalars().all()
        serialized_plan = {"title": plan.title, "steps": [{"title": step.title} for step in steps]}
    assistant_payload = deterministic_reply(
        payload.content, {"recommendations": recommendations, "action_plan": serialized_plan}
    )
    assistant_message = ChatMessage(
        session_id=session.id,
        user_id=current_user.id,
        role="assistant",
        content=assistant_payload["content"],
        citations=assistant_payload["citations"],
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)
    return serialize_message(assistant_message)


@router.get("/sessions/{session_id}/stream")
async def stream_session(
    session_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    session = (
        await db.execute(
            select(ChatSession).where(ChatSession.id == uuid.UUID(session_id), ChatSession.user_id == current_user.id)
        )
    ).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesion no encontrada")

    async def event_stream() -> AsyncGenerator[str, None]:
        messages = await list_messages(session_id, current_user, db)
        for message in messages[-10:]:
            yield f"data: {json.dumps(message.model_dump())}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
