from crewai import Agent

from app.agents.crew.llm import get_groq_llm


def create_evaluation_agent() -> Agent:
    llm = get_groq_llm()
    kwargs = {"llm": llm} if llm else {}
    return Agent(
        role="Evaluation Agent",
        goal="Interpret model metrics and explain model quality in practical language.",
        backstory="You read training reports and explain accuracy, ROC-AUC, precision, recall, and confusion matrices.",
        allow_delegation=False,
        verbose=False,
        **kwargs,
    )
