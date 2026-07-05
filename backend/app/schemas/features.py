from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FeatureReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    dataset_id: int
    engineered_dataset_path: str
    report_path: str
    report_json_path: str
    feature_summary: dict
    original_columns: int
    final_columns: int
    encoding_method: str
    scaling_method: str
    features_created: list[str]
    dropped_columns: list[str]
    target_column: str | None
    created_at: datetime
