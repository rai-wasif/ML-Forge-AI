import html
import json
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.cleaning_report import CleaningReport
from app.models.eda_report import EDAReport
from app.models.feature_report import FeatureReport
from app.models.training_report import TrainingReport
from app.rag.config import DEFAULT_COLLECTION
from app.rag.indexing.indexer import index_documents


REPORTS_ROOT = Path(__file__).resolve().parents[1] / "storage" / "reports" / "final"


def generate_final_report(db: Session, training_report_id: int) -> dict:
    training_report = get_training_report_or_404(db, training_report_id)
    dataset = training_report.dataset
    project = training_report.project
    report_dir = REPORTS_ROOT / f"project_{project.id:03d}" / f"dataset_{dataset.id:03d}" / f"training_{training_report.id:03d}"
    report_dir.mkdir(parents=True, exist_ok=True)

    context = build_report_context(db, training_report)
    markdown = render_markdown_report(context)
    html_content = render_html_report(markdown, context)

    markdown_path = report_dir / "final_ai_report.md"
    html_path = report_dir / "final_ai_report.html"
    metadata_path = report_dir / "final_ai_report.json"

    markdown_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(html_content, encoding="utf-8")

    qdrant_status = index_report_for_research(markdown_path)
    payload = {
        "training_report_id": training_report.id,
        "project_id": project.id,
        "dataset_id": dataset.id,
        "markdown_path": str(markdown_path),
        "html_path": str(html_path),
        "html_url": report_url(html_path),
        "qdrant": qdrant_status,
        "recommendations": context["recommendations"],
    }
    metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    artifacts = dict(training_report.artifacts or {})
    artifacts["final_report"] = payload
    training_report.artifacts = artifacts
    training_report.final_report_path = str(markdown_path)

    log_activity(
        db,
        project.id,
        "AI Report Generated",
        f"Final AI report generated for '{dataset.name}'.",
    )
    db.commit()
    db.refresh(training_report)
    return payload


def build_report_context(db: Session, training_report: TrainingReport) -> dict:
    dataset = training_report.dataset
    project = training_report.project
    latest_eda = latest_report(db, EDAReport, dataset.id)
    latest_cleaning = latest_report(db, CleaningReport, dataset.id)
    latest_features = latest_report(db, FeatureReport, dataset.id)
    experiments = list_project_experiments(db, project.id)
    shap_summary = (training_report.artifacts or {}).get("shap", {})

    return {
        "project": project,
        "dataset": dataset,
        "eda": latest_eda,
        "cleaning": latest_cleaning,
        "features": latest_features,
        "training": training_report,
        "experiments": experiments,
        "shap": shap_summary,
        "recommendations": build_recommendations(training_report, shap_summary, experiments),
    }


def render_markdown_report(context: dict) -> str:
    project = context["project"]
    dataset = context["dataset"]
    training = context["training"]
    eda = context["eda"]
    cleaning = context["cleaning"]
    features = context["features"]
    shap_summary = context["shap"]
    metrics = training.metrics.get("best", {})

    lines = [
        f"# MLForge AI Final Report: {project.name}",
        "",
        "## Dataset Overview",
        "",
        f"- Dataset: {dataset.name}",
        f"- Rows: {dataset.row_count}",
        f"- Columns: {dataset.column_count}",
        f"- Missing values: {dataset.missing_values}",
        f"- Duplicate rows: {dataset.duplicate_rows}",
        "",
    ]

    if eda:
        overview = eda.report_data.get("dataset_overview", {})
        lines.extend(
            [
                "## EDA Summary",
                "",
                f"- Total missing values: {overview.get('total_missing_values', 0)}",
                f"- Duplicate percentage: {overview.get('duplicate_percentage', 0)}%",
                f"- Visualizations generated: {len(eda.visualizations or [])}",
                "",
            ]
        )

    if cleaning:
        lines.extend(
            [
                "## Cleaning Summary",
                "",
                f"- Missing values: {cleaning.missing_values_before} -> {cleaning.missing_values_after}",
                f"- Duplicates removed: {cleaning.duplicates_removed}",
                f"- Outliers handled: {cleaning.outliers_handled}",
                "",
            ]
        )

    if features:
        lines.extend(
            [
                "## Feature Engineering Summary",
                "",
                f"- Columns: {features.original_columns} -> {features.final_columns}",
                f"- Encoding: {features.encoding_method}",
                f"- Scaling: {features.scaling_method}",
                f"- Created features: {', '.join(features.features_created or []) or 'None'}",
                f"- Dropped columns: {', '.join(features.dropped_columns or []) or 'None'}",
                "",
            ]
        )

    lines.extend(
        [
            "## Model Selection",
            "",
            f"- Problem type: {training.problem_type}",
            f"- Target column: {training.target_column}",
            f"- Best model: {training.best_model}",
            f"- Training time: {training.training_time:.3f}s",
            f"- MLflow run ID: {training.mlflow_run_id or 'Not logged'}",
            "",
            "## Best Metrics",
            "",
            *[f"- {key}: {value}" for key, value in metrics.items() if key != "confusion_matrix"],
            "",
            "## Model Comparison",
            "",
            "| Model | Score | Training Time | Inference Time |",
            "| --- | ---: | ---: | ---: |",
            *[
                f"| {row.get('model')} | {row.get('score')} | {row.get('training_time')} | {row.get('inference_time')} |"
                for row in training.metrics.get("comparison", [])
            ],
            "",
            "## SHAP Explainability",
            "",
        ]
    )

    if shap_summary.get("top_features"):
        lines.extend(
            [
                f"- Method: {shap_summary.get('method', 'shap')}",
                f"- Sample rows: {shap_summary.get('sample_rows', 0)}",
                "",
                "| Feature | Importance |",
                "| --- | ---: |",
                *[
                    f"| {item['feature']} | {item['importance']} |"
                    for item in shap_summary.get("top_features", [])[:15]
                ],
                "",
            ]
        )
    else:
        lines.extend(["- SHAP analysis was not available for this run.", ""])

    lines.extend(
        [
            "## Recommendations",
            "",
            *[f"- {item}" for item in context["recommendations"]],
            "",
            "## Experiment History",
            "",
            "| Run | Best Model | Score | Training Time | Created |",
            "| --- | --- | ---: | ---: | --- |",
            *[
                f"| {item['id']} | {item['best_model']} | {item['score']} | {item['training_time']} | {item['created_at']} |"
                for item in context["experiments"][:8]
            ],
            "",
        ]
    )

    return "\n".join(lines)


def render_html_report(markdown: str, context: dict) -> str:
    training = context["training"]
    shap_summary = context["shap"]
    escaped = html.escape(markdown)
    shap_image = ""
    if shap_summary.get("importance_url"):
        shap_image = f"<img src='{html.escape(shap_summary['importance_url'])}' alt='SHAP feature importance' />"

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>MLForge AI Final Report</title>
    <style>
      body {{ margin: 0; padding: 32px; font-family: Arial, sans-serif; color: #18211f; background: #f6f7f4; }}
      main {{ max-width: 1100px; margin: 0 auto; background: #fff; border: 1px solid #d9ded8; border-radius: 8px; padding: 24px; }}
      h1 {{ margin-top: 0; }}
      pre {{ white-space: pre-wrap; line-height: 1.55; font-family: inherit; }}
      img {{ max-width: 100%; border: 1px solid #d9ded8; border-radius: 6px; margin: 16px 0; }}
      .meta {{ color: #66736f; font-weight: 700; }}
    </style>
  </head>
  <body>
    <main>
      <p class="meta">Training report #{training.id}</p>
      {shap_image}
      <pre>{escaped}</pre>
    </main>
  </body>
</html>
"""


def build_recommendations(training_report: TrainingReport, shap_summary: dict, experiments: list[dict]) -> list[str]:
    recommendations = []
    metrics = training_report.metrics.get("best", {})

    if training_report.problem_type == "classification":
        roc_auc = metrics.get("roc_auc")
        f1 = metrics.get("f1_score")
        if roc_auc is not None and roc_auc < 0.75:
            recommendations.append("Improve ranking quality by adding domain features or tuning class imbalance handling.")
        if f1 is not None and f1 < 0.75:
            recommendations.append("Review precision and recall tradeoffs before using the model in a decision workflow.")
    else:
        r2 = metrics.get("r2")
        if r2 is not None and r2 < 0.6:
            recommendations.append("Try stronger feature engineering or target transformations to improve regression fit.")

    top_features = shap_summary.get("top_features", [])[:3]
    if top_features:
        names = ", ".join(item["feature"] for item in top_features)
        recommendations.append(f"Focus model review on the strongest drivers: {names}.")

    if len(experiments) >= 2:
        current = experiments[0]["score"]
        previous = experiments[1]["score"]
        if current is not None and previous is not None:
            direction = "improved" if current >= previous else "declined"
            recommendations.append(f"Latest experiment {direction} versus the previous run ({current} vs {previous}).")

    if not recommendations:
        recommendations.append("Use this run as a baseline and compare it against future experiments.")

    return recommendations


def latest_report(db: Session, model, dataset_id: int):
    return db.scalars(
        select(model)
        .where(model.dataset_id == dataset_id)
        .order_by(model.created_at.desc())
    ).first()


def list_project_experiments(db: Session, project_id: int) -> list[dict]:
    reports = db.scalars(
        select(TrainingReport)
        .where(TrainingReport.project_id == project_id)
        .order_by(TrainingReport.created_at.desc())
    ).all()

    return [experiment_payload(report) for report in reports]


def experiment_payload(report: TrainingReport) -> dict:
    metrics = report.metrics.get("best", {})
    return {
        "id": report.id,
        "dataset_id": report.dataset_id,
        "best_model": report.best_model,
        "problem_type": report.problem_type,
        "target_column": report.target_column,
        "score": best_score(report),
        "accuracy": metrics.get("accuracy"),
        "roc_auc": metrics.get("roc_auc"),
        "f1_score": metrics.get("f1_score"),
        "rmse": metrics.get("rmse"),
        "r2": metrics.get("r2"),
        "training_time": report.training_time,
        "mlflow_run_id": report.mlflow_run_id,
        "experiment_name": report.mlflow_experiment_name,
        "final_report_path": report.final_report_path,
        "created_at": report.created_at.isoformat(),
    }


def best_score(report: TrainingReport) -> float | None:
    comparison = report.metrics.get("comparison", [])
    for row in comparison:
        if row.get("model") == report.best_model:
            return row.get("score")
    metrics = report.metrics.get("best", {})
    return metrics.get("roc_auc") or metrics.get("accuracy") or metrics.get("r2")


def index_report_for_research(path: Path) -> dict:
    try:
        return index_documents(
            [path],
            collection_name=DEFAULT_COLLECTION,
            include_knowledge=False,
            include_reports=False,
        )
    except Exception as exc:
        return {"status": "failed", "error": str(exc), "collection": DEFAULT_COLLECTION}


def report_url(path: Path) -> str:
    relative = path.relative_to(REPORTS_ROOT.parent).as_posix()
    return f"/reports/{relative}"


def get_training_report_or_404(db: Session, report_id: int) -> TrainingReport:
    report = db.get(TrainingReport, report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training report not found.",
        )
    return report


def log_activity(db: Session, project_id: int, activity_type: str, message: str | None = None) -> Activity:
    activity = Activity(
        project_id=project_id,
        activity_type=activity_type,
        message=message,
    )
    db.add(activity)
    return activity
