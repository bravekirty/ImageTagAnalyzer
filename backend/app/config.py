from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    REDIS_HOST: str
    REDIS_PORT: int

    SECRET_KEY: str
    ALGORITHM: str

    IMAGGA_API_URL: str
    IMAGGA_API_KEY: str
    IMAGGA_API_SECRET: str

    class Config:
        env_file = ".env"


settings = Settings()
