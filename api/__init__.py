from fastapi import APIRouter

from api.health.health import health_router
from api.game.game import game_router
from api.user.user import user_router

from core.config import config

router = APIRouter(prefix=config.api_prefix)


router.include_router(health_router, tags=['Health'])
router.include_router(game_router, tags=['Game'])
router.include_router(user_router, tags=['User'])

__all__ = ["router"]
