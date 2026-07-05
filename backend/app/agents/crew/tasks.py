from crewai import Task


def create_pipeline_tasks(agents: dict) -> list[Task]:
    return [
        Task(
            description="Plan which ML pipeline stages are needed for the user request.",
            expected_output="A clear ordered plan of agents and tools to use.",
            agent=agents["planner"],
        ),
        Task(
            description="Inspect dataset metadata and validate that downstream ML stages can run.",
            expected_output="Dataset readiness summary.",
            agent=agents["dataset"],
        ),
        Task(
            description="Run and interpret EDA if requested by the planner.",
            expected_output="EDA summary with key observations.",
            agent=agents["eda"],
        ),
        Task(
            description="Run cleaning if requested by the planner.",
            expected_output="Cleaning summary with missing values, duplicates, and outliers.",
            agent=agents["cleaning"],
        ),
        Task(
            description="Generate features if requested by the planner.",
            expected_output="Feature engineering summary.",
            agent=agents["feature"],
        ),
        Task(
            description="Train models if requested by the planner.",
            expected_output="Training result and best model recommendation.",
            agent=agents["training"],
        ),
        Task(
            description="Interpret metrics and produce a concise final recommendation.",
            expected_output="Readable evaluation summary.",
            agent=agents["evaluation"],
        ),
    ]
