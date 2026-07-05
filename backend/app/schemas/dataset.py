from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    file_path: str | None
    file_type: str | None
    file_size_bytes: int
    row_count: int
    column_count: int
    column_names: list[str]
    data_types: dict[str, str]
    missing_values: int
    missing_values_by_column: dict[str, int]
    duplicate_rows: int
    memory_usage_bytes: int
    created_at: datetime
