from typing import List

from pydantic import BaseModel


class EventDTO(BaseModel):
    id: int    
    description: str
    price: int

class CompanyDTO(BaseModel):
    id: int
    name: str
    description: str
    price: int
    thumbnail: str
    events: List[EventDTO]

class GameDTO(BaseModel):
    id: int
    theme: str
    companies: List[CompanyDTO]
    users: List["UserDTO"]
    started: bool

class UserDTO(BaseModel):
    id: int
    nickname: str
    gold: int

    games: List["GameDTO"]

class CreateGameDTO(BaseModel):
    theme: str

class TradeDTO(BaseModel):
    company_id: int
    amount: int

class CreateTradeDTO(BaseModel):
    trades: List[TradeDTO]
