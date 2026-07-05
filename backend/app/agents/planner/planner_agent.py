from crewai import Agent

from app.agents.crew.llm import get_groq_llm


def create_planner_agent() -> Agent:
    llm = get_groq_llm()
    kwargs = {"llm": llm} if llm else {}
    return Agent(
        role="ML Pipeline Planner",
        goal="Plan the correct ML workflow from the user's natural language request.",
        backstory=(
            "You coordinate dataset, EDA, cleaning, feature engineering, training, "
            "evaluation, and documentation agents. You never perform ML work directly."
        ),
        allow_delegation=True,
        verbose=False,
        **kwargs,
    )
