from crewai import Agent

from app.agents.crew.llm import get_groq_llm


def create_documentation_agent() -> Agent:
    llm = get_groq_llm()
    kwargs = {"llm": llm} if llm else {}
    return Agent(
        role="Documentation Agent",
        goal="Create concise markdown summaries of ML experiments and recommendations.",
        backstory="You turn pipeline outputs into readable documentation for humans and future agents.",
        allow_delegation=False,
        verbose=False,
        **kwargs,
    )
