from typing import List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship

from app.services.game_service import Company as CompanyModel
from core.entities.schema.db import Base
from datetime import datetime


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    companies: Mapped[List["Company"]] = relationship(back_populates='game')

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    game: Mapped["Game"] = relationship(back_populates="companies")

    name = mapped_column(String)
    description = mapped_column(String)
    price: Mapped[int] = mapped_column()

    events: Mapped[List["Event"]] = relationship(back_populates="company")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    day: Mapped[int] = mapped_column()

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship(back_populates="events")


def create_game(
    db: Session,
    companies: List[CompanyModel],
) -> Game:
    game = Game()
    game.companies = []
    for c in companies:
        comp = Company()
        comp.name = c.name
        comp.description = c.description
        comp.price = c.price
        game.companies.append(comp)

    db.add(game)
    db.commit()
    db.refresh(game)
    return game
