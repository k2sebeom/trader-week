from typing import Annotated, Union

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi import Cookie

from sqlalchemy.orm import Session

from core.entities.schema.db import get_db
from core.entities.schema.game import get_or_create_user, User, get_user_by_id
from core.entities.dto.user import SignInUserDTO
from core.entities.dto.game import UserDTO
from core.entities.dto.convert import user_to_dto

user_router = APIRouter(prefix='/user')


@user_router.post("/signin")
async def signin_new_user(req: SignInUserDTO, resp: Response, db: Session = Depends(get_db)) -> UserDTO:
    user = get_or_create_user(db, req.nickname, req.password)
    if user is None:
        raise HTTPException(401, f'Password mismatch')
    resp.set_cookie(key='user_id', value=user.id, expires=3600)
    return user_to_dto(user)


@user_router.get("/me")
async def get_me(db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None) -> UserDTO:
    if user_id is None:
        raise HTTPException(401, 'Not signed in')
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(404, f'User not found')
    return user_to_dto(user)
