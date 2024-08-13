from typing import List

from pydantic import BaseModel

from core.entities.dto.user import UserDTO

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
    users: List[UserDTO]


class CreateGameDTO(BaseModel):
    theme: str

class TradeDTO(BaseModel):
    company_id: int
    amount: int

class CreateTradeDTO(BaseModel):
    trades: List[TradeDTO]
