from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: str

    FRONTEND_URL: str

    ANALYZE_SERVICE_URL: str
    ANALYTICS_SERVICE_URL: str
    SAMPLE_SERVICE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
