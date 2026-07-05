from crewai import Agent

from app.agents.crew.llm import get_groq_llm


def create_training_agent() -> Agent:
    llm = get_groq_llm()
    kwargs = {"llm": llm} if llm else {}
    return Agent(
        role="Training Agent",
        goal="Train candidate models, compare metrics, and save the best model.",
        backstory="You call the AutoML training pipeline and summarize the best model recommendation.",
        allow_delegation=False,
        verbose=False,
        **kwargs,
    )
