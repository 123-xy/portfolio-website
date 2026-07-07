from fastapi import APIRouter

from app.interfaces.api.v1.routers import auth, health

# Aggregate router for API v1. Feature routers (applications, uploads, officer,
# reports, audit) are mounted here as they land in later phases.
api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
