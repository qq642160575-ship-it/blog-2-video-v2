from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Environment
    environment: str = "development"

    # Database
    database_url: str

    # Redis
    redis_url: str

    # OpenAI Compatible API
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"

    # Azure Speech
    azure_speech_key: str = ""
    azure_speech_region: str = "eastus"

    # Storage
    storage_path: str = "./storage"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
