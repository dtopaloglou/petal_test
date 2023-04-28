import os
from typing import Optional

from pydantic import BaseSettings, Field
from functools import lru_cache

ROOT_DIR = os.path.dirname(os.path.abspath(".run.sh"))


class Database(BaseSettings):
    user: str = Field(..., env="DB_USER")
    password: str = Field(..., env="DB_PASSWORD")
    port: Optional[str] = Field(5432, env="DB_PORT")
    db: str = Field(..., env="DB_DB")
    host: Optional[str] = Field("localhost", env="DB_HOST")


class Settings(BaseSettings):
    app_name: str = "Petal"
    app_description: str = "Petal API"
    environment: str = Field(..., env="ENVIRONMENT")
    openapi_url: str = "/openapi.json"


    database: Database = Database()


@lru_cache()
def settings() -> Settings:
    return Settings()
