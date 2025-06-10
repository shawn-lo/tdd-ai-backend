from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TDD AI Assistant Backend"

    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # AI Model Settings
    OPENAI_API_KEY: str

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 