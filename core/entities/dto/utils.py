from typing import List
from datetime import datetime, timedelta

from core.entities.schema.game import Game, Trade, Company, Event, User
from core.entities.dto.game import GameDTO, CompanyDTO, EventDTO, UserDTO


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
        started=game.started_at is not None,
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

def user_to_dto(user: User) -> UserDTO:
    return UserDTO(
        id=user.id,
        nickname=user.nickname,
        gold=user.gold,

        games=[
            game_to_dto(g) for g in user.games
        ]
    )