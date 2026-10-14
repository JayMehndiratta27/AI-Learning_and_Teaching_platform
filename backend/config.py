"""Application configuration loaded from environment variables."""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # auto | mongo | sqlite — auto uses Mongo when reachable, else embedded SQLite (no install).
    database_mode: str = "auto"
    sqlite_path: str = "data/learnflow.db"
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "learnflow"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    openai_api_key: str = ""
    cors_origins: str = "http://localhost:4200"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
