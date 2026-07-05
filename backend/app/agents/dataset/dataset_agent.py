from crewai import Agent

from app.agents.crew.llm import get_groq_llm


def create_dataset_agent() -> Agent:
    llm = get_groq_llm()
    kwargs = {"llm": llm} if llm else {}
    return Agent(
        role="Dataset Agent",
        goal="Understand uploaded datasets, validate metadata, and identify likely targets.",
        backstory="You inspect dataset metadata and prepare context for downstream ML agents.",
        allow_delegation=False,
        verbose=False,
        **kwargs,
    )
