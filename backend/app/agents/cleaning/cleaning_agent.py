from crewai import Agent

from app.agents.crew.llm import get_groq_llm


def create_cleaning_agent() -> Agent:
    llm = get_groq_llm()
    kwargs = {"llm": llm} if llm else {}
    return Agent(
        role="Cleaning Agent",
        goal="Run preprocessing, fix data quality issues, and summarize cleaning actions.",
        backstory="You call the cleaning pipeline for missing values, duplicates, invalid values, and outliers.",
        allow_delegation=False,
        verbose=False,
        **kwargs,
    )
