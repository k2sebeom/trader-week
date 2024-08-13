from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from core.entities.schema.db import get_db
from core.entities.schema.game import get_or_create_user, User
from core.entities.dto.user import SignInUserDTO, UserDTO

user_router = APIRouter(prefix='/user')

def user_to_dto(user: User) -> UserDTO:
    return UserDTO(
        id=user.id,
        nickname=user.nickname,
        gold=user.gold,
    )

@user_router.post("/signin")
async def signin_new_user(req: SignInUserDTO, resp: Response, db: Session = Depends(get_db)) -> UserDTO:
    user = get_or_create_user(db, req.nickname, req.password)
    if user is None:
        raise HTTPException(401, f'Password mismatch')
    resp.set_cookie(key='user_id', value=user.id)
    return user_to_dto(user)
