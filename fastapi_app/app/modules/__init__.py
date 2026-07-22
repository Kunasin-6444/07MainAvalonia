from fastapi import APIRouter
from app.modules.health import health_router
from app.modules.pos import pos_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(pos_router)

__all__ = ["api_v1_router", "health_router", "pos_router"]
