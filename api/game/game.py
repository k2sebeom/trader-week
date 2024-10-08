from datetime import datetime, timedelta
from pytz import utc
from typing import Annotated, Union, List

from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session

from app.services.game_service import GameService, GameException
from core.entities.schema.db import get_db
from core.entities.schema.game import (
    create_game,
    get_game_by_id,
    get_user_by_id,
    get_last_game,
    get_all_games,
)
from core.entities.schema.game import create_trades
from core.entities.dto.game import GameDTO, CreateGameDTO
from core.entities.dto.game import CreateTradeDTO, HoldingsDTO, GameResultDTO
from core.entities.dto.convert import game_to_dto

game_router = APIRouter(prefix="/game")

game_service = GameService()


@game_router.post("/")
async def post_new_game(
    req: CreateGameDTO, db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None
) -> GameDTO:
    if user_id is None:
        raise HTTPException(401, "Not signed in")
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(401, "Not signed in")

    game = get_last_game(db)
    if game is not None and datetime.now(utc) - game.created_at < timedelta(minutes=2):
        raise HTTPException(400, "New Game can be only created per minute")

    companies, theme = await game_service.get_companies(theme=req.theme, language=req.language)
    await game_service.create_new_events(companies, language=req.language)
    game = create_game(db, theme, user, companies, req.language)

    game.users.append(user)
    db.commit()
    return game_to_dto(game)


@game_router.get("/")
def get_games(language: str, db=Depends(get_db)) -> List[GameDTO]:
    games = get_all_games(db, language)
    return [game_to_dto(game) for game in games]


@game_router.get("/{id}")
async def get_game(id: int, db=Depends(get_db)) -> GameDTO:
    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, "Game not found")
    return game_to_dto(game)


@game_router.put("/{id}/start")
async def start_game(
    id: int, db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None
) -> GameDTO:
    if user_id is None:
        raise HTTPException(401, "Not signed in")

    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, "Game not found")

    if game.owner_id != user_id:
        raise HTTPException(401, "Not authorized to start the game")

    if game.started_at is not None:
        raise HTTPException(400, f"Game {id} already started at {game.started_at}")

    game_service.start_game(game)
    db.commit()
    return game_to_dto(game)


@game_router.put("/{id}/join")
async def join_game(
    id: int, db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None
) -> GameDTO:
    if user_id is None:
        raise HTTPException(401, "Not signed in")
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(401, "Not signed in")

    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, f"Game with id {id} not found")
    if game.started_at is not None:
        raise HTTPException(403, "Cannot join started game")

    if user not in game.users:
        game.users.append(user)
        if game.owner_id is None:
            game.owner_id = user.id
        db.commit()
    return game_to_dto(game)


@game_router.delete("/{id}/leave")
async def leave_game(
    id: int, db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None
) -> GameDTO:
    if user_id is None:
        raise HTTPException(401, "Not signed in")
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(401, "Not signed in")

    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, f"Game with id {id} not found")

    if game.started:
        raise HTTPException(403, "Cannot leave a started game")

    # If owner is leaving
    game.users.remove(user)
    if game.owner_id == user.id:
        if len(game.users) > 0:
            game.owner_id = game.users[0].id

    db.commit()
    return game_to_dto(game)


@game_router.post("/{id}/trade")
async def make_trade(
    id: int, req: CreateTradeDTO, db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None
) -> HoldingsDTO:
    if user_id is None:
        raise HTTPException(401, "Not signed in")
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(401, "Not signed in")

    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, f"Game with id {id} not found")
    if game.started_at is None or user_id not in [u.id for u in game.users]:
        raise HTTPException(403, "Not allowed to make trade in this game")

    if datetime.now(utc) - game.started_at > timedelta(minutes=2 * 8):
        raise HTTPException(403, "Market closed")

    try:
        trades = game_service.perform_trades(user, game, req.trades)
    except GameException as e:
        raise HTTPException(400, e)
    trades = create_trades(db, trades)

    db.refresh(game)
    return HoldingsDTO(
        holdings=game.get_holdings(user),
        gold=user.gold,
    )


@game_router.get("/{id}/result")
async def get_result(id: int, db: Session = Depends(get_db)) -> GameResultDTO:
    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, f"Game with id {id} not found")
    if not game.closed:
        raise HTTPException(400, "Game is not closed yet")

    result = game_service.get_game_result(game)

    return GameResultDTO(result=result)


@game_router.put("/{id}/throw")
async def throw_all_stocks(
    id: int, db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None
) -> GameDTO:
    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, f"Game with id {id} not found")
    if not game.closed:
        raise HTTPException(400, "Game is not closed yet")

    if user_id is None:
        raise HTTPException(401, "Not signed in")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(404, f"User {user_id} not found")

    game_service.throws_all_stocks(game, user)
    db.commit()
    db.refresh(game)
    return game_to_dto(game)
