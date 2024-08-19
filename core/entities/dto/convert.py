from core.entities.schema.game import Game, Trade, Company, User
from core.entities.dto.game import GameDTO, TradeDTO, CompanyDTO, EventDTO, UserDTO, ParticipantDTO


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
        holdings=game.get_holdings(user),
    )


def company_to_dto(company: Company) -> CompanyDTO:
    price_history = company.prices
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
            for e in company.filtered_events
        ],
    )


def trade_to_dto(trade: Trade) -> TradeDTO:
    return TradeDTO(company_id=trade.company_id, user_id=trade.user_id, amount=trade.amount, day=trade.day)


def game_to_dto(game: Game) -> GameDTO:
    return GameDTO(
        id=game.id,
        theme=game.theme,
        started=game.started,
        started_at=game.started_at,
        companies=[company_to_dto(c) for c in game.companies],
        participants=[user_to_participant(user, game) for user in game.users],
        trades=[trade_to_dto(trade) for trade in game.trades],
    )
