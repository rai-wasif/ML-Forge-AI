import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")


class Settings:
    database_url: str
    groq_api_key: str
    google_api_key: str

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()
