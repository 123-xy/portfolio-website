from fastapi import APIRouter

from app.interfaces.api.v1.routers import analytics, applications, auth, health, officer, reports

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(applications.router)
api_router.include_router(officer.router)
api_router.include_router(reports.router)
api_router.include_router(analytics.router)
