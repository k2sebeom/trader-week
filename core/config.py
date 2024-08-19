import dotenv

from pydantic_settings import BaseSettings

import os

dotenv.load_dotenv()


class Config(BaseSettings):
    api_prefix: str = "/api"
    port: int = int(os.getenv("PORT") or "8080")

    openai_key: str = os.getenv("OPENAI_KEY") or ""

    database_url: str = os.getenv("DATABASE_URL") or "postgresql://localhost:5432"

    thumbnails_path: str = os.getenv("THUMBNAILS_PATH") or "thumbnails"


config: Config = Config()
