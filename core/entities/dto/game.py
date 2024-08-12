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
    events: List[EventDTO]

class GameDTO(BaseModel):
    id: int
    theme: str
    companies: List[CompanyDTO]


class CreateGameDTO(BaseModel):
    theme: str
