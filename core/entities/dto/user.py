from pydantic import BaseModel


class SignInUserDTO(BaseModel):
    nickname: str
    password: str
