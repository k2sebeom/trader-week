import os
from typing import Dict, Any, List

from pydantic_settings import BaseSettings
import yaml


config_path = os.getenv("API_CONFIG_PATH") or "traders.yml"
with open(config_path, "r") as f:
    cfg: Dict[str, Any] = yaml.safe_load(f)


class Config(BaseSettings):
    api_prefix: str = "/api"
    port: int = cfg.get("port", 8080)

    openai_key: str = cfg.get("openai_key", "")
    getimgai_key: str = cfg.get("getimgai_key", "")

    database_url: str = cfg.get("database_url", "postgresql://localhost:5432")

    thumbnails_path: str = cfg.get("thumbnails_path", "thumbnails")

    allowed_origins: List[str] = cfg.get("allowed_origins", [])


config: Config = Config()
