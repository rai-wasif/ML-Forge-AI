from crewai import Agent

from app.agents.crew.llm import get_groq_llm


def create_eda_agent() -> Agent:
    llm = get_groq_llm()
    kwargs = {"llm": llm} if llm else {}
    return Agent(
        role="EDA Agent",
        goal="Run exploratory data analysis and explain important dataset patterns.",
        backstory="You call the EDA engine and translate statistics into concise ML insights.",
        allow_delegation=False,
        verbose=False,
        **kwargs,
    )
