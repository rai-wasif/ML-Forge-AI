from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EDAReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    dataset_id: int
    report_path: str
    report_json_path: str
    report_data: dict
    visualizations: list[dict]
    created_at: datetime
