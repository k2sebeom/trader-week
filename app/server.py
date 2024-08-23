from typing import List

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import router
from core.config import config


def init_routers(app_: FastAPI) -> None:
    app_.include_router(router)

    app_.mount("/thumbnails", StaticFiles(directory=config.thumbnails_path), name="thumbnails")


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=config.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ]
    return middleware


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="Trader Week API",
        description="API for Trader Week Web Game",
        version="0.1.0",
        docs_url="/docs",
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    return app_


app = create_app()
