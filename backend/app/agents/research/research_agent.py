from crewai import Agent

from app.agents.crew.llm import get_groq_llm


def create_research_agent() -> Agent:
    llm = get_groq_llm()
    kwargs = {"llm": llm} if llm else {}
    return Agent(
        role="Research Agent",
        goal="Explain ML algorithms, evaluation metrics, and modeling tradeoffs.",
        backstory="You provide general ML guidance before the RAG knowledge layer is added.",
        allow_delegation=False,
        verbose=False,
        **kwargs,
    )
