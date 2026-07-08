from fastapi import APIRouter

from app.interfaces.api.v1.routers import applications, auth, health

# Aggregate router for API v1. Feature routers (officer, reports, audit) are
# mounted here as they land in later phases.
api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(applications.router)
