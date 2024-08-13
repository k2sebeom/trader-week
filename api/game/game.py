from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.game_service import GameService
from core.entities.schema.db import get_db
from core.entities.schema.game import create_game, get_game_by_id, create_events, Game
from core.entities.dto.game import GameDTO, CompanyDTO, EventDTO, CreateGameDTO

game_router = APIRouter(prefix='/game')

game_service = GameService()

def game_to_dto(game: Game) -> GameDTO:
    now = datetime.now()
    return GameDTO(
        id=game.id,
        theme=game.theme,
        companies=[
            CompanyDTO(
                id=c.id,
                name=c.name,
                description=c.description,
                price=c.price,
                thumbnail=c.thumbnail,
                events=[
                    EventDTO(
                        id=e.id,
                        description=e.description,
                        price=e.price,
                    )
                    for e in filter(lambda e: (e.happen_at - now) < timedelta(seconds=0), c.events)
                ]
            )
            for c in game.companies
        ]
    )


@game_router.post("/")
async def post_new_game(req: CreateGameDTO, db = Depends(get_db)) -> GameDTO:
    companies = await game_service.get_companies(theme=req.theme)
    game = create_game(db, req.theme, companies)

    events = await game_service.create_new_events(game.companies)
    create_events(db, events)
    return game_to_dto(game)

@game_router.get("/{id}")
async def get_game(id: int, db = Depends(get_db)) -> GameDTO:
    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, 'Game not found')
    return game_to_dto(game)


@game_router.put("/{id}/start")
async def start_game(id: int, db: Session = Depends(get_db)) -> GameDTO:
    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, 'Game not found')

    if game.started_at is not None:
        raise HTTPException(400, f'Game {id} already started at {game.started_at}')

    now = datetime.now()
    game.started_at = now
    for c in game.companies:
        for i, e in enumerate(c.events):
            e.happen_at = now + timedelta(minutes=i * 2)
    db.commit()
    return game_to_dto(game)
