from fastapi import APIRouter

from app.services.game_service import GameService
from core.entities.schema.game import create_game

game_router = APIRouter(prefix='/game')

game_service = GameService()

@game_router.get("/companies")
async def get_companies():
    companies = game_service.get_companies()
    for c in companies:
        print(c)
        print(game_service.get_company_thumbnail(c))
    create_game()
    return companies
