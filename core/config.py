import dotenv

from pydantic import BaseSettings

import os

dotenv.load_dotenv()


class Config(BaseSettings):
    api_prefix: str = '/api'
    port: int = os.getenv('PORT')

config: Config = Config()