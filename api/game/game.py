from datetime import datetime, timedelta
from typing import Annotated, Union, List

from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session

from app.services.game_service import GameService
from core.entities.schema.db import get_db
from core.entities.schema.game import create_game, get_game_by_id, create_events, Game, get_user_by_id
from core.entities.schema.game import Trade, create_trades, Event
from core.entities.dto.game import GameDTO, CompanyDTO, EventDTO, CreateGameDTO, UserDTO
from core.entities.dto.game import CreateTradeDTO, TradeDTO

game_router = APIRouter(prefix='/game')

game_service = GameService()


def filter_events(events: List[Event]) -> List[Event]:
    now = datetime.now()
    return list(filter(lambda e: (e.happen_at - now) < timedelta(seconds=0), events))


def current_price(initial_price: int, events: List[Event]):
    for e in events:
        initial_price += int(initial_price * e.price / 100)
    return initial_price


def game_to_dto(game: Game) -> GameDTO:
    return GameDTO(
        id=game.id,
        theme=game.theme,
        companies=[
            CompanyDTO(
                id=c.id,
                name=c.name,
                description=c.description,
                price=current_price(c.price, filter_events(c.events)),
                thumbnail=c.thumbnail,
                events=[
                    EventDTO(
                        id=e.id,
                        description=e.description,
                        price=e.price,
                    )
                    for e in filter_events(c.events)
                ],
            )
            for c in game.companies
        ],
        users=[
            UserDTO(
                nickname=user.nickname,
                id=user.id,
                gold=user.gold,
            )
            for user in game.users
        ],
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
async def start_game(id: int, db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None) -> GameDTO:
    if user_id is None:
        raise HTTPException(401, 'Not signed in')
    
    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, 'Game not found')

    if len(game.users) == 0 or game.users[0].id != user_id:
        raise HTTPException(401, 'Not authorized to start the game')

    if game.started_at is not None:
        raise HTTPException(400, f'Game {id} already started at {game.started_at}')

    now = datetime.now()
    game.started_at = now
    for c in game.companies:
        for i, e in enumerate(c.events):
            e.happen_at = now + timedelta(minutes=i * 2)
    db.commit()
    return game_to_dto(game)


@game_router.put("/{id}/join")
async def join_game(id: int, db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None) -> GameDTO:
    if user_id is None:
        raise HTTPException(401, 'Not signed in')
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(401, 'Not signed in')

    game = get_game_by_id(db, id)
    game.users.append(user)
    db.commit()
    return game_to_dto(game)


@game_router.delete("/{id}/leave")
async def join_game(id: int, db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None) -> GameDTO:
    if user_id is None:
        raise HTTPException(401, 'Not signed in')
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(401, 'Not signed in')

    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, f'Game with id {id} not found')

    game.users.remove(user)
    db.commit()
    return game_to_dto(game)


@game_router.post("/{id}/trade")
async def make_trade(id: int, req: CreateTradeDTO, db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None) -> List[TradeDTO]:
    if user_id is None:
        raise HTTPException(401, 'Not signed in')
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(401, 'Not signed in')

    game = get_game_by_id(db, id)
    if game is None:
        raise HTTPException(404, f'Game with id {id} not found')
    if game.started_at is None or user_id not in [u.id for u in game.users]:
        raise HTTPException(403, 'Not allowed to make trade in this game')

    events = filter_events(game.companies[0].events)

    if datetime.now() - events[-1].happen_at > timedelta(seconds=115):
        raise HTTPException(403, 'Market closed')

    curr_day = len(events) + 1
    trades = []
    curr_gold = user.gold

    company_dict = {
        c.id: c
        for c in game.companies
    }
    holding = {
        c.id: 0
        for c in game.companies
    }
    for t in filter(lambda t: t.user_id == user_id, game.trades):
        holding[t.company_id] += t.amount

    for t in req.trades:
        if t.company_id in company_dict:
            events = filter_events(company_dict[t.company_id].events)
            price = current_price(company_dict[t.company_id].price, events) * t.amount
            if curr_gold < price:
                break
            if t.amount < 0 and holding[t.company_id] < -t.amount:
                continue
            curr_gold -= price
            trades.append(
                Trade(
                    user_id=user_id,
                    game_id=id,
                    company_id=t.company_id,
                    day=curr_day,
                    amount=t.amount,
                )
            )
    trades = create_trades(db, trades)
    user.gold = curr_gold
    db.commit()
    return trades
