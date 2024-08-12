from typing import List

from pydantic import BaseModel

class CompanyDTO(BaseModel):
    id: int
    name: str
    description: str
    price: int

class GameDTO(BaseModel):
    id: int
    companies: List[CompanyDTO]
