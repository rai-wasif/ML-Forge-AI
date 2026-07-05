from crewai import Agent

from app.agents.crew.llm import get_groq_llm


def create_feature_agent() -> Agent:
    llm = get_groq_llm()
    kwargs = {"llm": llm} if llm else {}
    return Agent(
        role="Feature Engineering Agent",
        goal="Generate machine-learning-ready features from cleaned datasets.",
        backstory="You call feature tools for type detection, encoding, scaling, and useful feature creation.",
        allow_delegation=False,
        verbose=False,
        **kwargs,
    )
