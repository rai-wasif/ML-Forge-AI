import os

from crewai import LLM

from app.core.config import get_settings


def get_groq_llm() -> LLM | None:
    settings = get_settings()
    if not settings.groq_api_key:
        os.environ.setdefault("OPENAI_API_KEY", "placeholder-not-used")
        return None

    try:
        return LLM(
            model="groq/llama-3.1-8b-instant",
            api_key=settings.groq_api_key,
        )
    except ImportError:
        os.environ.setdefault("OPENAI_API_KEY", "placeholder-not-used")
        return None
