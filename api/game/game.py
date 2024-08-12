from fastapi import APIRouter, Depends

from app.services.game_service import GameService
from core.entities.schema.db import get_db
from core.entities.schema.game import create_game
from core.entities.dto.game import GameDTO, CompanyDTO

game_router = APIRouter(prefix='/game')

game_service = GameService()

@game_router.post("/")
async def post_new_game(db = Depends(get_db)) -> GameDTO:
    companies = game_service.get_companies()
    game = create_game(db, companies)
    return GameDTO(
        id=game.id,
        companies=[
            CompanyDTO(
                id=c.id,
                name=c.name,
                description=c.description,
                price=c.price,
            )
            for c in game.companies
        ]
    )
