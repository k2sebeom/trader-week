from fastapi import APIRouter, Response


game_router = APIRouter(prefix='/game')


@game_router.get("/")
async def health():
    return Response(status_code=200)
