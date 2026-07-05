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
    mlflow_run_id: str | None = None
    mlflow_experiment_name: str | None = None
    mlflow_artifact_uri: str | None = None
    shap_summary_path: str | None = None
    shap_importance_path: str | None = None
    final_report_path: str | None = None
    artifacts: dict
    created_at: datetime


class ExperimentSummary(BaseModel):
    id: int
    dataset_id: int
    best_model: str
    problem_type: str
    target_column: str
    score: float | None = None
    accuracy: float | None = None
    roc_auc: float | None = None
    f1_score: float | None = None
    rmse: float | None = None
    r2: float | None = None
    training_time: float
    mlflow_run_id: str | None = None
    experiment_name: str | None = None
    final_report_path: str | None = None
    created_at: str


class ExperimentComparisonRead(BaseModel):
    project_id: int
    runs: list[ExperimentSummary]
    latest: ExperimentSummary | None = None
    previous: ExperimentSummary | None = None
    score_delta: float | None = None
    summary: str


class FinalReportRead(BaseModel):
    training_report_id: int
    project_id: int
    dataset_id: int
    markdown_path: str
    html_path: str
    html_url: str
    qdrant: dict
    recommendations: list[str]
