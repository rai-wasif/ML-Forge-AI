from crewai import Crew, Process

from app.agents.cleaning.cleaning_agent import create_cleaning_agent
from app.agents.crew.tasks import create_pipeline_tasks
from app.agents.dataset.dataset_agent import create_dataset_agent
from app.agents.documentation.documentation_agent import create_documentation_agent
from app.agents.eda.eda_agent import create_eda_agent
from app.agents.evaluation.evaluation_agent import create_evaluation_agent
from app.agents.feature.feature_agent import create_feature_agent
from app.agents.planner.planner_agent import create_planner_agent
from app.agents.training.training_agent import create_training_agent


def create_ml_engineer_crew() -> Crew:
    agents = {
        "planner": create_planner_agent(),
        "dataset": create_dataset_agent(),
        "eda": create_eda_agent(),
        "cleaning": create_cleaning_agent(),
        "feature": create_feature_agent(),
        "training": create_training_agent(),
        "evaluation": create_evaluation_agent(),
        "documentation": create_documentation_agent(),
    }
    tasks = create_pipeline_tasks(agents)

    return Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=False,
    )
