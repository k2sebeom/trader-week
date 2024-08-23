from typing import List, Optional, Dict
from datetime import datetime

from pydantic import BaseModel, Field


class EventDTO(BaseModel):
    id: int
    description: str
    price: int
    happen_at: datetime


class CompanyDTO(BaseModel):
    id: int
    name: str
    description: str
    price: int
    thumbnail: str
    events: List[EventDTO]
    history: List[int]


class HoldingsDTO(BaseModel):
    holdings: Dict[int, int]
    gold: int


class GameDTO(BaseModel):
    id: int
    theme: str
    companies: List[CompanyDTO]
    participants: List["ParticipantDTO"]
    trades: List["TradeDTO"]
    started: bool
    started_at: Optional[datetime]
    closed: bool
    owner_id: Optional[int]


class ParticipantDTO(BaseModel):
    id: int
    nickname: str
    gold: int
    holdings: Dict[int, int]


class UserDTO(BaseModel):
    id: int
    nickname: str
    gold: int


class TradeDTO(BaseModel):
    company_id: int
    user_id: int
    amount: int
    day: int


# Requests
class CreateGameDTO(BaseModel):
    theme: str
    language: str = Field(default="en")


class TradeReqDTO(BaseModel):
    company_id: int
    amount: int


class CreateTradeDTO(BaseModel):
    trades: List[TradeReqDTO]


class GameResultDTO(BaseModel):
    result: Dict[int, int]
