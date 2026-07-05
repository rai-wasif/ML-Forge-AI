import json
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.preprocessing.pipeline import run_cleaning_pipeline
from app.ml.preprocessing.report_generator import render_cleaning_report
from app.models.activity import Activity
from app.models.cleaning_report import CleaningReport
from app.models.dataset import Dataset
from app.services.dataset_service import read_dataframe


CLEANED_ROOT = Path(__file__).resolve().parents[1] / "storage" / "cleaned"
REPORTS_ROOT = Path(__file__).resolve().parents[1] / "storage" / "reports" / "cleaning"


def run_cleaning(db: Session, dataset_id: int, target_column: str | None = None) -> CleaningReport:
    dataset = get_dataset_or_404(db, dataset_id)
    dataset_path = Path(dataset.file_path or "")

    if not dataset_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset file was not found on disk.",
        )

    extension = f".{dataset.file_type}" if dataset.file_type else dataset_path.suffix.lower()
    dataframe = read_dataframe(dataset_path, extension)
    cleaned_dataframe, summary = run_cleaning_pipeline(dataframe, target_column)

    cleaned_dir = CLEANED_ROOT / f"project_{dataset.project_id:03d}" / f"dataset_{dataset.id:03d}"
    report_dir = REPORTS_ROOT / f"project_{dataset.project_id:03d}" / f"dataset_{dataset.id:03d}"
    cleaned_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    safe_stem = Path(dataset.name).stem.replace(" ", "_")
    cleaned_path = cleaned_dir / f"cleaned_{safe_stem}.csv"
    report_json_path = report_dir / "cleaning_report.json"
    report_html_path = report_dir / "cleaning_report.html"

    cleaned_dataframe.to_csv(cleaned_path, index=False)

    with report_json_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, allow_nan=False)

    report_html_path.write_text(
        render_cleaning_report(summary, dataset.name),
        encoding="utf-8",
    )

    report = CleaningReport(
        project_id=dataset.project_id,
        dataset_id=dataset.id,
        cleaned_dataset_path=str(cleaned_path),
        report_path=str(report_html_path),
        report_json_path=str(report_json_path),
        cleaning_summary=summary,
        original_rows=summary["original_rows"],
        final_rows=summary["final_rows"],
        original_columns=summary["original_columns"],
        final_columns=summary["final_columns"],
        missing_values_before=summary["missing_values_before"],
        missing_values_after=summary["missing_values_after"],
        duplicates_removed=summary["duplicates_removed"],
        outliers_handled=summary["outliers_handled"],
    )

    db.add(report)
    db.flush()
    log_activity(db, dataset.project_id, "Dataset Cleaned", f"Cleaned dataset generated for '{dataset.name}'.")
    db.commit()
    db.refresh(report)
    return report


def get_latest_report(db: Session, dataset_id: int) -> CleaningReport | None:
    return db.scalars(
        select(CleaningReport)
        .where(CleaningReport.dataset_id == dataset_id)
        .order_by(CleaningReport.created_at.desc())
    ).first()


def get_report_or_404(db: Session, report_id: int) -> CleaningReport:
    report = db.get(CleaningReport, report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cleaning report not found.",
        )
    return report


def get_dataset_or_404(db: Session, dataset_id: int) -> Dataset:
    dataset = db.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )
    return dataset


def log_activity(db: Session, project_id: int, activity_type: str, message: str | None = None) -> Activity:
    activity = Activity(
        project_id=project_id,
        activity_type=activity_type,
        message=message,
    )
    db.add(activity)
    return activity
