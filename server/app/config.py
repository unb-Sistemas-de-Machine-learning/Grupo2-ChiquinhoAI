from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str
    gemini_model_name: str = "gemini-flash-latest"
    qdrant_key: str | None = None
    qdrant_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return Settings()  # type: ignore
