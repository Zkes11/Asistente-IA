from fastapi import APIRouter

from app.api.routes import (
    action_plans,
    assessments,
    auth,
    chat,
    profile,
    programs,
    recommendations,
    system,
    universities,
)

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(programs.router, prefix="/programs", tags=["programs"])
api_router.include_router(universities.router, prefix="/universities", tags=["universities"])
api_router.include_router(action_plans.router, prefix="/action-plans", tags=["action_plans"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
