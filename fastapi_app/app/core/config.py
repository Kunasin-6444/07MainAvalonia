import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Nakhon Parts Dashboard API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "160747")
    DB_NAME: str = os.getenv("DB_NAME", "nakorndata")

    CORS_ORIGINS: List[str] = ["*"]


settings = Settings()
