from typing import Annotated, Union, List

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi import Cookie

from sqlalchemy.orm import Session

from core.entities.schema.db import get_db
from core.entities.schema.game import get_or_create_user, get_user_by_id, get_rankings
from core.entities.dto.user import SignInUserDTO
from core.entities.dto.game import UserDTO, GameDTO
from core.entities.dto.convert import user_to_dto, game_to_dto

user_router = APIRouter(prefix="/user")


@user_router.post("/signin")
async def signin_new_user(req: SignInUserDTO, resp: Response, db: Session = Depends(get_db)) -> UserDTO:
    user = get_or_create_user(db, req.nickname, req.password)
    if user is None:
        raise HTTPException(401, "Password mismatch")
    resp.set_cookie(key="user_id", value=str(user.id), expires=3600 * 24, httponly=True, secure=True)
    return user_to_dto(user)


@user_router.get("/me")
async def get_me(db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None) -> UserDTO:
    if user_id is None:
        raise HTTPException(401, "Not signed in")
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    return user_to_dto(user)


@user_router.get("/history")
async def get_history(
    db: Session = Depends(get_db), user_id: Annotated[Union[int, None], Cookie()] = None
) -> List[GameDTO]:
    if user_id is None:
        raise HTTPException(401, "Not signed in")
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    return [game_to_dto(g) for g in filter(lambda g: g.closed, user.games)]


@user_router.get("/ranking")
async def get_ranking(db: Session = Depends(get_db)) -> List[UserDTO]:
    ranking = get_rankings(db)
    return [user_to_dto(u) for u in ranking]
