from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None

    class Config:
        env_file = ".env"