import json
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.training.pipeline import run_training_pipeline
from app.ml.training.report_generator import render_training_report
from app.models.activity import Activity
from app.models.dataset import Dataset
from app.models.feature_report import FeatureReport
from app.models.training_report import TrainingReport


MODELS_ROOT = Path(__file__).resolve().parents[1] / "storage" / "models"
REPORTS_ROOT = Path(__file__).resolve().parents[1] / "storage" / "reports" / "training"


def train_dataset(db: Session, dataset_id: int, target_column: str | None = None) -> TrainingReport:
    dataset = get_dataset_or_404(db, dataset_id)
    feature_report = get_latest_feature_report(db, dataset_id)

    if feature_report is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Generate features before training a model.",
        )

    target = target_column or feature_report.target_column
    if not target:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target column could not be detected.",
        )

    feature_dataset_path = Path(feature_report.engineered_dataset_path)
    if not feature_dataset_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature dataset file was not found on disk.",
        )

    model_dir = MODELS_ROOT / f"project_{dataset.project_id:03d}" / f"dataset_{dataset.id:03d}"
    report_dir = REPORTS_ROOT / f"project_{dataset.project_id:03d}" / f"dataset_{dataset.id:03d}"
    report_dir.mkdir(parents=True, exist_ok=True)

    try:
        summary = run_training_pipeline(
            feature_dataset_path,
            target,
            model_dir,
            feature_report.feature_summary,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Training failed: {exc}",
        ) from exc

    report_json_path = report_dir / "training_report.json"
    report_html_path = report_dir / "training_report.html"

    with report_json_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, allow_nan=False)

    report_html_path.write_text(render_training_report(summary), encoding="utf-8")

    report = TrainingReport(
        project_id=dataset.project_id,
        dataset_id=dataset.id,
        problem_type=summary["problem_type"],
        target_column=summary["target_column"],
        selected_models=summary["selected_models"],
        best_model=summary["best_model"],
        metrics=summary["metrics"],
        training_time=summary["training_time"],
        model_path=summary["artifacts"]["model_path"],
        report_path=str(report_html_path),
        report_json_path=str(report_json_path),
        artifacts=summary["artifacts"],
    )

    db.add(report)
    db.flush()
    log_activity(db, dataset.project_id, "Model Trained", f"Best model '{report.best_model}' trained for '{dataset.name}'.")
    db.commit()
    db.refresh(report)
    return report


def get_latest_report(db: Session, dataset_id: int) -> TrainingReport | None:
    return db.scalars(
        select(TrainingReport)
        .where(TrainingReport.dataset_id == dataset_id)
        .order_by(TrainingReport.created_at.desc())
    ).first()


def get_report_or_404(db: Session, report_id: int) -> TrainingReport:
    report = db.get(TrainingReport, report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training report not found.",
        )
    return report


def get_latest_feature_report(db: Session, dataset_id: int) -> FeatureReport | None:
    return db.scalars(
        select(FeatureReport)
        .where(FeatureReport.dataset_id == dataset_id)
        .order_by(FeatureReport.created_at.desc())
    ).first()


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
