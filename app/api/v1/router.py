"""
Main API v1 router that aggregates all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, rag

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    tags=["Health"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    rag.router,
    prefix="/rag",
    tags=["RAG Operations"]
)
