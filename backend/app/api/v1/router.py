from fastapi import APIRouter

from app.api.v1 import (
    chat,
    checklists,
    documents,
    eligibility,
    health,
    profiles,
    rules,
    scholarships,
    schemes,
    sources,
    users,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(profiles.router)
api_router.include_router(scholarships.router)
api_router.include_router(schemes.router)
api_router.include_router(sources.router)
api_router.include_router(rules.router)
api_router.include_router(documents.router)
api_router.include_router(checklists.router)
api_router.include_router(chat.router)
api_router.include_router(eligibility.router)
