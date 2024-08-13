from pydantic import BaseModel

class UserDTO(BaseModel):
    id: int
    nickname: str
    gold: int


class SignInUserDTO(BaseModel):
    nickname: str
    password: str
