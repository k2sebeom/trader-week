from fastapi import APIRouter

from api.health.health import health_router

from core.config import config

router = APIRouter(prefix=config.api_prefix)


router.include_router(health_router, tags=['Health'])

__all__ = ["router"]
