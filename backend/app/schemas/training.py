from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TrainingReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    dataset_id: int
    problem_type: str
    target_column: str
    selected_models: list[str]
    best_model: str
    metrics: dict
    training_time: float
    model_path: str
    report_path: str
    report_json_path: str
    artifacts: dict
    created_at: datetime
