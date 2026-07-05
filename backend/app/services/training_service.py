import json
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.explainability.shap_analyzer import generate_shap_report
from app.ml.tracking import log_training_run
from app.ml.training.pipeline import run_training_pipeline
from app.ml.training.report_generator import render_training_report
from app.models.activity import Activity
from app.models.dataset import Dataset
from app.models.feature_report import FeatureReport
from app.models.training_report import TrainingReport
from app.services import report_service


MODELS_ROOT = Path(__file__).resolve().parents[1] / "storage" / "models"
REPORTS_ROOT = Path(__file__).resolve().parents[1] / "storage" / "reports" / "training"
SHAP_ROOT = Path(__file__).resolve().parents[1] / "storage" / "reports" / "shap"


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
    artifacts = dict(summary["artifacts"])
    shap_summary = run_shap_analysis(
        feature_dataset_path=feature_dataset_path,
        target_column=target,
        model_path=artifacts["model_path"],
        project_id=dataset.project_id,
        dataset_id=dataset.id,
    )
    artifacts["shap"] = shap_summary
    summary["artifacts"] = artifacts

    mlflow_result = log_training_run(
        project_name=dataset.project.name,
        dataset_name=dataset.name,
        summary=summary,
        artifact_paths=collect_artifact_paths(report_html_path, report_json_path, artifacts),
    )
    artifacts["mlflow"] = mlflow_result
    with report_json_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, allow_nan=False)

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
        mlflow_run_id=mlflow_result.get("run_id"),
        mlflow_experiment_name=mlflow_result.get("experiment_name"),
        mlflow_artifact_uri=mlflow_result.get("artifact_uri"),
        shap_summary_path=shap_summary.get("summary_path"),
        shap_importance_path=shap_summary.get("importance_path"),
        artifacts=artifacts,
    )

    db.add(report)
    db.flush()
    log_activity(db, dataset.project_id, "Model Trained", f"Best model '{report.best_model}' trained for '{dataset.name}'.")
    db.commit()
    db.refresh(report)

    try:
        report_service.generate_final_report(db, report.id)
        db.refresh(report)
    except Exception as exc:
        artifacts = dict(report.artifacts or {})
        artifacts["final_report"] = {"status": "failed", "error": str(exc)}
        report.artifacts = artifacts
        db.commit()
        db.refresh(report)

    return report


def get_latest_report(db: Session, dataset_id: int) -> TrainingReport | None:
    return db.scalars(
        select(TrainingReport)
        .where(TrainingReport.dataset_id == dataset_id)
        .order_by(TrainingReport.created_at.desc())
    ).first()


def list_project_experiments(db: Session, project_id: int) -> list[dict]:
    return report_service.list_project_experiments(db, project_id)


def compare_project_experiments(db: Session, project_id: int) -> dict:
    experiments = list_project_experiments(db, project_id)
    latest = experiments[0] if experiments else None
    previous = experiments[1] if len(experiments) > 1 else None
    delta = None

    if latest and previous and latest.get("score") is not None and previous.get("score") is not None:
        delta = round(float(latest["score"]) - float(previous["score"]), 6)

    return {
        "project_id": project_id,
        "runs": experiments,
        "latest": latest,
        "previous": previous,
        "score_delta": delta,
        "summary": comparison_summary(latest, previous, delta),
    }


def generate_final_report(db: Session, report_id: int) -> dict:
    return report_service.generate_final_report(db, report_id)


def get_report_or_404(db: Session, report_id: int) -> TrainingReport:
    report = db.get(TrainingReport, report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training report not found.",
        )
    return report


def run_shap_analysis(
    feature_dataset_path: Path,
    target_column: str,
    model_path: str,
    project_id: int,
    dataset_id: int,
) -> dict:
    shap_dir = SHAP_ROOT / f"project_{project_id:03d}" / f"dataset_{dataset_id:03d}"
    try:
        return generate_shap_report(
            model_path=model_path,
            feature_dataset_path=feature_dataset_path,
            target_column=target_column,
            output_dir=shap_dir,
        )
    except Exception as exc:
        shap_dir.mkdir(parents=True, exist_ok=True)
        error_path = shap_dir / "shap_error.json"
        payload = {"status": "failed", "error": str(exc)}
        error_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload


def collect_artifact_paths(report_html_path: Path, report_json_path: Path, artifacts: dict) -> list[Path]:
    paths = [
        Path(artifacts["model_path"]),
        Path(artifacts["preprocessing_pipeline_path"]),
        Path(artifacts["feature_pipeline_path"]),
        Path(artifacts["label_encoder_path"]),
        report_html_path,
        report_json_path,
    ]

    shap_payload = artifacts.get("shap", {})
    for key in ("summary_path", "importance_path", "json_path"):
        if shap_payload.get(key):
            paths.append(Path(shap_payload[key]))

    return paths


def comparison_summary(latest: dict | None, previous: dict | None, delta: float | None) -> str:
    if latest is None:
        return "No training experiments found for this project."

    if previous is None:
        return f"Only one experiment exists. Latest best model is {latest['best_model']} with score {latest['score']}."

    if delta is None:
        return "Latest and previous experiments are available, but score comparison was not possible."

    direction = "improved" if delta >= 0 else "declined"
    return (
        f"Latest run {direction} by {abs(delta)} score points. "
        f"Latest best model: {latest['best_model']}; previous best model: {previous['best_model']}."
    )


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
