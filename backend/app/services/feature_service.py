import json
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.feature_engineering.pipeline import run_feature_pipeline
from app.ml.feature_engineering.report_generator import render_feature_report
from app.models.activity import Activity
from app.models.cleaning_report import CleaningReport
from app.models.dataset import Dataset
from app.models.feature_report import FeatureReport


ENGINEERED_ROOT = Path(__file__).resolve().parents[1] / "storage" / "engineered"
REPORTS_ROOT = Path(__file__).resolve().parents[1] / "storage" / "reports" / "features"


def generate_features(db: Session, dataset_id: int, target_column: str | None = None) -> FeatureReport:
    dataset = get_dataset_or_404(db, dataset_id)
    cleaning_report = get_latest_cleaning_report(db, dataset_id)

    if cleaning_report is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Run dataset cleaning before generating features.",
        )

    cleaned_path = Path(cleaning_report.cleaned_dataset_path)
    if not cleaned_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cleaned dataset file was not found on disk.",
        )

    dataframe = read_cleaned_dataframe(cleaned_path)
    engineered_dataframe, summary = run_feature_pipeline(dataframe, target_column)

    engineered_dir = ENGINEERED_ROOT / f"project_{dataset.project_id:03d}" / f"dataset_{dataset.id:03d}"
    report_dir = REPORTS_ROOT / f"project_{dataset.project_id:03d}" / f"dataset_{dataset.id:03d}"
    engineered_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    engineered_path = engineered_dir / "feature_dataset.parquet"
    report_json_path = report_dir / "feature_report.json"
    report_html_path = report_dir / "feature_report.html"

    engineered_dataframe.to_parquet(engineered_path, index=False)

    with report_json_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, allow_nan=False)

    report_html_path.write_text(
        render_feature_report(summary, dataset.name),
        encoding="utf-8",
    )

    report = FeatureReport(
        project_id=dataset.project_id,
        dataset_id=dataset.id,
        engineered_dataset_path=str(engineered_path),
        report_path=str(report_html_path),
        report_json_path=str(report_json_path),
        feature_summary=summary,
        original_columns=summary["original_columns"],
        final_columns=summary["final_columns"],
        encoding_method=summary["encoding_method"],
        scaling_method=summary["scaling_method"],
        features_created=summary["features_created"],
        dropped_columns=summary["dropped_columns"],
        target_column=summary.get("target_column"),
    )

    db.add(report)
    db.flush()
    log_activity(db, dataset.project_id, "Features Generated", f"Feature dataset generated for '{dataset.name}'.")
    db.commit()
    db.refresh(report)
    return report


def get_latest_report(db: Session, dataset_id: int) -> FeatureReport | None:
    return db.scalars(
        select(FeatureReport)
        .where(FeatureReport.dataset_id == dataset_id)
        .order_by(FeatureReport.created_at.desc())
    ).first()


def get_report_or_404(db: Session, report_id: int) -> FeatureReport:
    report = db.get(FeatureReport, report_id)
    if report is None:
        raise_report_not_found()
    return report


def raise_report_not_found():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Feature report not found.",
    )


def get_dataset_or_404(db: Session, dataset_id: int) -> Dataset:
    dataset = db.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )
    return dataset


def get_latest_cleaning_report(db: Session, dataset_id: int) -> CleaningReport | None:
    return db.scalars(
        select(CleaningReport)
        .where(CleaningReport.dataset_id == dataset_id)
        .order_by(CleaningReport.created_at.desc())
    ).first()


def read_cleaned_dataframe(path: Path):
    if path.suffix.lower() == ".parquet":
        import pandas as pd

        return pd.read_parquet(path)

    import pandas as pd

    return pd.read_csv(path)


def log_activity(db: Session, project_id: int, activity_type: str, message: str | None = None) -> Activity:
    activity = Activity(
        project_id=project_id,
        activity_type=activity_type,
        message=message,
    )
    db.add(activity)
    return activity
