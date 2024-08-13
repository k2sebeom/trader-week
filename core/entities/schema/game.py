from typing import List, Optional

from sqlalchemy import String, ForeignKey, exists, Table, Column
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship
import bcrypt

from core.entities.schema.db import Base
from datetime import datetime, timedelta

INITIAL_GOLD = 10_000

# For User - Game association
association_table = Table(
    "users_games",
    Base.metadata,
    Column("left_id", ForeignKey("users.id"), primary_key=True),
    Column("right_id", ForeignKey("games.id"), primary_key=True),
)

class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)

    theme: Mapped[str] = mapped_column(default='')
    companies: Mapped[List["Company"]] = relationship(back_populates='game')

    users: Mapped[List["User"]] = relationship(
        secondary=association_table, back_populates="games",
    )
    trades: Mapped[List["Trade"]] = relationship()

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    started_at: Mapped[datetime] = mapped_column(nullable=True)


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    game: Mapped["Game"] = relationship(back_populates="companies")

    thumbnail: Mapped[str] = mapped_column(String)

    name = mapped_column(String)
    description = mapped_column(String)
    price: Mapped[int] = mapped_column()

    events: Mapped[List["Event"]] = relationship(back_populates="company")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    day: Mapped[int] = mapped_column()

    description: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()

    happen_at: Mapped[datetime] = mapped_column()

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship(back_populates="events")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    nickname: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()

    gold: Mapped[int] = mapped_column()
    games: Mapped[List["Game"]] = relationship(
        secondary=association_table, back_populates="users",
    )


class Trade(Base):
    __tablename__ = "trades"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    amount: Mapped[int] = mapped_column()


def create_game(
    db: Session,
    theme: str,
    companies: List[Company],
) -> Game:
    game = Game(theme=theme, companies=companies)
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

def create_events(
    db: Session,
    events: List[Event],
) -> Game:
    open_at = datetime.now() + timedelta(hours=1)
    for e in events:
        e.happen_at = open_at
        db.add(e)
    db.commit()
    return events

def get_game_by_id(
        db: Session,
        id: int
    ) -> Optional[Game]:
    if db.query(exists(Game).where(Game.id == id)).scalar():
        return db.query(Game).where(Game.id == id).scalar()
    else:
        return None

def get_or_create_user(
        db: Session,
        nickname: str,
        password: str,
    ) -> Optional[User]:
    if db.query(exists(User)).where(User.nickname == nickname).scalar():
        user: User = db.query(User).where(User.nickname == nickname).scalar()
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return user
        return None
    else:
        hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(
            nickname=nickname,
            password=hash.decode('utf-8'),
            gold=INITIAL_GOLD,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
