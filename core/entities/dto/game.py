from typing import List, Optional, Dict
from datetime import datetime

from pydantic import BaseModel


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
    users: List["ParticipantDTO"]
    trades: List['TradeDTO']
    started: bool
    started_at: Optional[datetime]

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
    amount: int


# Requests
class CreateGameDTO(BaseModel):
    theme: str

class CreateTradeDTO(BaseModel):
    trades: List[TradeDTO]
