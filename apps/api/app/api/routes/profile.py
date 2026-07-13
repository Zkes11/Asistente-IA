from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models import DataExport, DeletionRequest, User, UserProfile
from app.db.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest

router = APIRouter()


@router.get("", response_model=ProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> ProfileResponse:
    profile = (
        await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    ).scalar_one()
    return ProfileResponse(
        preferred_name=current_user.preferred_name,
        grade_level=profile.grade_level,
        country=profile.country,
        city=profile.city,
        goal=profile.goal,
        known_areas=profile.known_areas,
        onboarding_completed=profile.onboarding_completed,
        privacy_policy_accepted=profile.privacy_policy_accepted,
        assessment_consent=profile.assessment_consent,
        guardian_consent_required=profile.guardian_consent_required,
        guardian_consent_granted=profile.guardian_consent_granted,
    )


@router.patch("", response_model=ProfileResponse)
async def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    profile = (
        await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    ).scalar_one()
    update_data = payload.model_dump(exclude_unset=True)
    if "preferred_name" in update_data:
        current_user.preferred_name = update_data["preferred_name"]
    for field, value in update_data.items():
        if field != "preferred_name":
            setattr(profile, field, value)
    await db.commit()
    return await get_profile(current_user, db)


async def export_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    profile = await get_profile(current_user, db)
    payload: dict[str, object] = {
        "user": {"id": str(current_user.id), "email": current_user.email},
        "profile": profile.model_dump(),
    }
    export_record = DataExport(user_id=current_user.id, payload=payload)
    db.add(export_record)
    await db.commit()
    return payload


@router.delete("", response_model=MessageResponse)
async def delete_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> MessageResponse:
    current_user.deleted_at = datetime.now(UTC)
    db.add(DeletionRequest(user_id=current_user.id))
    await db.commit()
    return MessageResponse(message="Solicitud de eliminacion registrada")
