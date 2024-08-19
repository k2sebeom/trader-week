from typing import List, Dict
from datetime import datetime, timedelta

from core.entities.schema.game import Game, Trade, Company, Event, User
from core.entities.dto.game import GameDTO, CompanyDTO, EventDTO, UserDTO, ParticipantDTO
from core.utils.game import filter_events, get_prices, get_holdings


def user_to_dto(user: User) -> UserDTO:
    return UserDTO(
        id=user.id,
        nickname=user.nickname,
        gold=user.gold,
    )

def user_to_participant(user: User, game: Game) -> ParticipantDTO:
    return ParticipantDTO(
        id=user.id,
        nickname=user.nickname,
        gold=user.gold,
        holdings=get_holdings(user.id, game.companies, game.trades)
    )

def company_to_dto(company: Company) -> CompanyDTO:
    events = filter_events(company.events, company.game.started)
    price_history = get_prices(company.price, events)
    return CompanyDTO(
        id=company.id,
        name=company.name,
        description=company.description,
        price=price_history[-1],
        history=price_history,
        thumbnail=company.thumbnail,
        events=[
            EventDTO(
                id=e.id,
                description=e.description,
                price=e.price,
                happen_at=e.happen_at,
            )
            for e in events
        ],
    )


def game_to_dto(game: Game) -> GameDTO:
    return GameDTO(
        id=game.id,
        theme=game.theme,
        started=game.started_at is not None,
        started_at=game.started_at,
        companies=[
            company_to_dto(c)
            for c in game.companies
        ],
        users=[
            user_to_participant(user, game)
            for user in game.users
        ],
        holdings={
            user.id: get_holdings(user.id, game.companies, game.trades)
            for user in game.users
        }
    )
