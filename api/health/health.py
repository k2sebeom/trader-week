from fastapi import APIRouter, Response


health_router = APIRouter(prefix='/health')


@health_router.get("/")
async def health():
    return Response(status_code=200)
