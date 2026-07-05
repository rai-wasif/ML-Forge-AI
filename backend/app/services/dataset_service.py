import re
import shutil
from pathlib import Path

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.dataset import Dataset
from app.models.project import Project


ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".parquet"}
STORAGE_ROOT = Path(__file__).resolve().parents[1] / "storage" / "uploaded"


def upload_dataset(db: Session, project_id: int, file: UploadFile) -> Dataset:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    original_name = Path(file.filename or "").name
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only csv, xlsx, and parquet files are allowed.",
        )

    project_folder = STORAGE_ROOT / f"project_{project_id:03d}"
    project_folder.mkdir(parents=True, exist_ok=True)

    stored_name = _safe_filename(original_name)
    destination = project_folder / stored_name

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        metadata = extract_metadata(destination, extension)
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dataset metadata extraction failed: {exc}",
        ) from exc

    dataset = Dataset(
        project_id=project_id,
        name=original_name,
        file_path=str(destination),
        file_type=extension.lstrip("."),
        file_size_bytes=metadata["file_size_bytes"],
        row_count=metadata["row_count"],
        column_count=metadata["column_count"],
        column_names=metadata["column_names"],
        data_types=metadata["data_types"],
        missing_values=metadata["missing_values"],
        missing_values_by_column=metadata["missing_values_by_column"],
        duplicate_rows=metadata["duplicate_rows"],
        memory_usage_bytes=metadata["memory_usage_bytes"],
    )

    db.add(dataset)
    db.flush()
    log_activity(db, project_id, "Dataset Uploaded", f"Dataset '{dataset.name}' was uploaded.")
    log_activity(db, project_id, "Metadata Generated", f"Metadata generated for '{dataset.name}'.")
    db.commit()
    db.refresh(dataset)
    return dataset


def list_project_datasets(db: Session, project_id: int) -> list[Dataset]:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    return list(
        db.scalars(
            select(Dataset)
            .where(Dataset.project_id == project_id)
            .order_by(Dataset.created_at.desc())
        )
    )


def extract_metadata(path: Path, extension: str) -> dict:
    dataframe = read_dataframe(path, extension)
    missing_by_column = dataframe.isna().sum().to_dict()

    return {
        "file_size_bytes": path.stat().st_size,
        "row_count": int(len(dataframe)),
        "column_count": int(len(dataframe.columns)),
        "column_names": [str(column) for column in dataframe.columns],
        "data_types": {str(column): str(dtype) for column, dtype in dataframe.dtypes.items()},
        "missing_values": int(sum(missing_by_column.values())),
        "missing_values_by_column": {str(column): int(count) for column, count in missing_by_column.items()},
        "duplicate_rows": int(dataframe.duplicated().sum()),
        "memory_usage_bytes": int(dataframe.memory_usage(deep=True).sum()),
    }


def read_dataframe(path: Path, extension: str) -> pd.DataFrame:
    if extension == ".csv":
        return pd.read_csv(path)

    if extension == ".xlsx":
        return pd.read_excel(path)

    if extension == ".parquet":
        return pd.read_parquet(path)

    raise ValueError("Unsupported file type.")


def log_activity(db: Session, project_id: int, activity_type: str, message: str | None = None) -> Activity:
    activity = Activity(
        project_id=project_id,
        activity_type=activity_type,
        message=message,
    )
    db.add(activity)
    return activity


def _safe_filename(filename: str) -> str:
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("._")
    return safe_name or "dataset"
