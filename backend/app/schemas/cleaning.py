from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CleaningReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    dataset_id: int
    cleaned_dataset_path: str
    report_path: str
    report_json_path: str
    cleaning_summary: dict
    original_rows: int
    final_rows: int
    original_columns: int
    final_columns: int
    missing_values_before: int
    missing_values_after: int
    duplicates_removed: int
    outliers_handled: int
    created_at: datetime
