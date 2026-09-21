"""
V1 API router — aggregates all sub-routers under the /api/v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1.access_grants import router as access_router
from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.patients import router as patients_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(patients_router)
api_v1_router.include_router(access_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(documents_router)

