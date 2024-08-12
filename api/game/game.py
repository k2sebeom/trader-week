from fastapi import APIRouter, Depends, HTTPException

from app.services.game_service import GameService, Company, Event
from core.entities.schema.db import get_db
from core.entities.schema.game import create_game, get_game_by_id, create_events, Game
from core.entities.dto.game import GameDTO, CompanyDTO, EventDTO

game_router = APIRouter(prefix='/game')

game_service = GameService()

def game_to_dto(game: Game) -> GameDTO: 
    return GameDTO(
        id=game.id,
        companies=[
            CompanyDTO(
                id=c.id,
                name=c.name,
                description=c.description,
                price=c.price,
                events=[
                    EventDTO(
                        id=e.id,
                        description=e.description,
                        price=e.price,
                    )
                    for e in c.events
                ]
            )
            for c in game.companies
        ]
    )


@game_router.post("/")
async def post_new_game(db = Depends(get_db)) -> GameDTO:
    companies = game_service.get_companies()
    game = create_game(db, companies)
    return game_to_dto(game)


@game_router.post("/{id}/event")
async def post_new_event(id: int, db = Depends(get_db)) -> GameDTO:
    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, 'Game not found')
    events = game_service.create_new_events(game.companies)
    create_events(db, events)
    game = get_game_by_id(db, id)
    return game_to_dto(game)
