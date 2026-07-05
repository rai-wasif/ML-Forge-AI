from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.schemas.agents import AgentChatRequest, AgentChatResponse
from app.rag.config import DEFAULT_COLLECTION
from app.services import cleaning_service, eda_service, feature_service, rag_service, training_service


AGENT_REPORT_ROOT = Path(__file__).resolve().parents[1] / "storage" / "reports" / "agents"


def chat(db: Session, request: AgentChatRequest) -> AgentChatResponse:
    dataset = resolve_dataset(db, request.dataset_id, request.project_id)
    force = should_force(request.message)
    plan = build_plan(request.message)
    stages = {"dataset": dataset_stage(dataset)}

    if "experiments" in plan:
        stages["experiments"] = experiment_comparison_stage(db, dataset.project_id)

    if "eda" in plan:
        stages["eda"] = run_or_reuse_eda(db, dataset.id, force)

    if "cleaning" in plan:
        if "eda" not in stages:
            stages["eda"] = run_or_reuse_eda(db, dataset.id, False)
        stages["cleaning"] = run_or_reuse_cleaning(db, dataset.id, force)

    if "features" in plan:
        if "cleaning" not in stages:
            stages["cleaning"] = run_or_reuse_cleaning(db, dataset.id, False)
        stages["features"] = run_or_reuse_features(db, dataset.id, force)

    if "training" in plan:
        if "features" not in stages:
            stages["features"] = run_or_reuse_features(db, dataset.id, False)
        stages["training"] = run_or_reuse_training(db, dataset.id, force)
        stages["evaluation"] = evaluation_stage(stages["training"])

    if "research" in plan:
        stages["research"] = research_stage(request.message)

    message = build_response(plan, stages)
    documentation_path = write_documentation(dataset, request.message, plan, stages, message)

    return AgentChatResponse(
        message=message,
        plan=plan,
        dataset_id=dataset.id,
        project_id=dataset.project_id,
        stages=stages,
        artifacts={"documentation_path": str(documentation_path)},
    )


def resolve_dataset(db: Session, dataset_id: int | None, project_id: int | None) -> Dataset:
    if dataset_id is not None:
        dataset = db.get(Dataset, dataset_id)
    elif project_id is not None:
        dataset = db.scalars(
            select(Dataset)
            .where(Dataset.project_id == project_id)
            .order_by(Dataset.created_at.desc())
        ).first()
    else:
        dataset = db.scalars(select(Dataset).order_by(Dataset.created_at.desc())).first()

    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dataset was found for the agent request.",
        )

    return dataset


def build_plan(message: str) -> list[str]:
    lowered = message.lower()

    if is_experiment_comparison_request(lowered):
        return ["dataset", "experiments", "research", "documentation"]

    if any(word in lowered for word in ("train", "model", "best model", "automl", "predict")):
        plan = ["dataset", "eda", "cleaning", "features", "training", "evaluation", "documentation"]
        return add_research_if_needed(plan, lowered)

    if any(word in lowered for word in ("feature", "engineer", "prepare")):
        plan = ["dataset", "eda", "cleaning", "features", "documentation"]
        return add_research_if_needed(plan, lowered)

    if any(word in lowered for word in ("clean", "preprocess", "missing", "outlier")):
        plan = ["dataset", "eda", "cleaning", "documentation"]
        return add_research_if_needed(plan, lowered)

    if any(word in lowered for word in ("eda", "analyze", "analysis", "profile")):
        plan = ["dataset", "eda", "documentation"]
        return add_research_if_needed(plan, lowered)

    return add_research_if_needed(["dataset", "documentation"], lowered)


def is_experiment_comparison_request(lowered_message: str) -> bool:
    comparison_terms = ("compare", "previous", "experiment", "run history", "today")
    tracking_terms = ("experiment", "run", "mlflow", "previous", "history")
    return any(term in lowered_message for term in comparison_terms) and any(
        term in lowered_message for term in tracking_terms
    )


def add_research_if_needed(plan: list[str], lowered_message: str) -> list[str]:
    research_terms = (
        "why",
        "explain",
        "compare",
        "interpret",
        "recommend",
        "roc",
        "auc",
        "metric",
        "logistic",
        "xgboost",
        "overfit",
        "underfit",
        "feature importance",
    )

    if not any(term in lowered_message for term in research_terms):
        return plan

    output = list(plan)
    if "research" not in output:
        output.insert(max(len(output) - 1, 0), "research")
    return output


def should_force(message: str) -> bool:
    lowered = message.lower()
    return any(word in lowered for word in ("rerun", "again", "fresh", "retrain", "regenerate", "force"))


def dataset_stage(dataset: Dataset) -> dict:
    return {
        "agent": "Dataset Agent",
        "status": "completed",
        "dataset_name": dataset.name,
        "rows": dataset.row_count,
        "columns": dataset.column_count,
        "missing_values": dataset.missing_values,
        "duplicates": dataset.duplicate_rows,
    }


def run_or_reuse_eda(db: Session, dataset_id: int, force: bool) -> dict:
    report = None if force else eda_service.get_latest_report(db, dataset_id)
    status_label = "reused"
    if report is None:
        report = eda_service.analyze_dataset(db, dataset_id)
        status_label = "completed"

    overview = report.report_data["dataset_overview"]
    return {
        "agent": "EDA Agent",
        "status": status_label,
        "report_id": report.id,
        "rows": overview["rows"],
        "columns": overview["columns"],
        "missing_values": overview["total_missing_values"],
        "duplicates": overview["duplicate_rows"],
        "visualizations": len(report.visualizations),
    }


def run_or_reuse_cleaning(db: Session, dataset_id: int, force: bool) -> dict:
    report = None if force else cleaning_service.get_latest_report(db, dataset_id)
    status_label = "reused"
    if report is None:
        report = cleaning_service.run_cleaning(db, dataset_id)
        status_label = "completed"

    return {
        "agent": "Cleaning Agent",
        "status": status_label,
        "report_id": report.id,
        "missing_before": report.missing_values_before,
        "missing_after": report.missing_values_after,
        "duplicates_removed": report.duplicates_removed,
        "outliers_handled": report.outliers_handled,
        "cleaned_dataset_path": report.cleaned_dataset_path,
    }


def run_or_reuse_features(db: Session, dataset_id: int, force: bool) -> dict:
    report = None if force else feature_service.get_latest_report(db, dataset_id)
    status_label = "reused"
    if report is None:
        report = feature_service.generate_features(db, dataset_id)
        status_label = "completed"

    return {
        "agent": "Feature Agent",
        "status": status_label,
        "report_id": report.id,
        "original_columns": report.original_columns,
        "final_columns": report.final_columns,
        "encoding_method": report.encoding_method,
        "scaling_method": report.scaling_method,
        "features_created": report.features_created,
        "dropped_columns": report.dropped_columns,
        "target_column": report.target_column,
        "engineered_dataset_path": report.engineered_dataset_path,
    }


def run_or_reuse_training(db: Session, dataset_id: int, force: bool) -> dict:
    report = None if force else training_service.get_latest_report(db, dataset_id)
    status_label = "reused"
    if report is None:
        report = training_service.train_dataset(db, dataset_id)
        status_label = "completed"

    best_metrics = report.metrics.get("best", {})
    return {
        "agent": "Training Agent",
        "status": status_label,
        "report_id": report.id,
        "problem_type": report.problem_type,
        "target_column": report.target_column,
        "selected_models": report.selected_models,
        "best_model": report.best_model,
        "best_metrics": best_metrics,
        "training_time": report.training_time,
        "model_path": report.model_path,
    }


def evaluation_stage(training: dict) -> dict:
    metrics = training.get("best_metrics", {})
    if training.get("problem_type") == "classification":
        interpretation = (
            f"The best model reached accuracy {metrics.get('accuracy')} "
            f"and ROC-AUC {metrics.get('roc_auc')}, so it is a usable baseline."
        )
    else:
        interpretation = (
            f"The best model reached RMSE {metrics.get('rmse')} "
            f"and R2 {metrics.get('r2')}."
        )

    return {
        "agent": "Evaluation Agent",
        "status": "completed",
        "interpretation": interpretation,
    }


def experiment_comparison_stage(db: Session, project_id: int) -> dict:
    comparison = training_service.compare_project_experiments(db, project_id)
    return {
        "agent": "Experiment Analyst Agent",
        "status": "completed",
        "summary": comparison["summary"],
        "score_delta": comparison["score_delta"],
        "latest": comparison["latest"],
        "previous": comparison["previous"],
        "runs": comparison["runs"][:5],
    }


def research_stage(prompt: str) -> dict:
    try:
        result = rag_service.query_knowledge(prompt, DEFAULT_COLLECTION, top_k=3)
        sources = [
            {
                "title": source.get("title") or source.get("source", "Knowledge source"),
                "score": round(source.get("score", 0.0), 3),
                "source": source.get("source", ""),
            }
            for source in result["sources"]
        ]
        return {
            "agent": "Research Agent",
            "status": "completed",
            "answer": result["answer"],
            "sources": sources,
        }
    except Exception as exc:
        return {
            "agent": "Research Agent",
            "status": "unavailable",
            "answer": f"Knowledge-base research was skipped: {exc}",
            "sources": [],
        }


def build_response(plan: list[str], stages: dict) -> str:
    dataset = stages["dataset"]
    lines = [
        "ML Engineer Crew completed the request.",
        f"Dataset: {dataset['dataset_name']} ({dataset['rows']} rows, {dataset['columns']} columns).",
    ]

    if "eda" in stages:
        eda = stages["eda"]
        lines.append(
            f"EDA {eda['status']}: {eda['missing_values']} missing values, "
            f"{eda['duplicates']} duplicates, {eda['visualizations']} visualizations."
        )

    if "cleaning" in stages:
        cleaning = stages["cleaning"]
        lines.append(
            f"Cleaning {cleaning['status']}: missing {cleaning['missing_before']} -> "
            f"{cleaning['missing_after']}, duplicates removed {cleaning['duplicates_removed']}, "
            f"outliers handled {cleaning['outliers_handled']}."
        )

    if "features" in stages:
        features = stages["features"]
        lines.append(
            f"Features {features['status']}: columns {features['original_columns']} -> "
            f"{features['final_columns']}, target {features['target_column']}."
        )

    if "training" in stages:
        training = stages["training"]
        metrics = training["best_metrics"]
        metric_text = (
            f"accuracy {metrics.get('accuracy')}, ROC-AUC {metrics.get('roc_auc')}"
            if training["problem_type"] == "classification"
            else f"RMSE {metrics.get('rmse')}, R2 {metrics.get('r2')}"
        )
        lines.append(
            f"Training {training['status']}: detected {training['problem_type']}, "
            f"best model {training['best_model']} with {metric_text}."
        )

    if "evaluation" in stages:
        lines.append(stages["evaluation"]["interpretation"])

    if "experiments" in stages:
        experiments = stages["experiments"]
        lines.append(f"Experiment comparison: {experiments['summary']}")

    if "research" in stages:
        research = stages["research"]
        lines.append(f"Research {research['status']}: {research['answer']}")

    lines.append("Manual buttons are still available for debugging each stage.")
    return "\n".join(lines)


def write_documentation(dataset: Dataset, prompt: str, plan: list[str], stages: dict, message: str) -> Path:
    output_dir = AGENT_REPORT_ROOT / f"project_{dataset.project_id:03d}" / f"dataset_{dataset.id:03d}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "agent_summary.md"

    content = [
        "# ML Engineer Crew Summary",
        "",
        f"Prompt: {prompt}",
        "",
        "## Plan",
        "",
        *[f"- {step}" for step in plan],
        "",
        "## Result",
        "",
        message,
        "",
        "## Stage Data",
        "",
    ]

    for name, data in stages.items():
        content.append(f"### {name.title()}")
        content.append("")
        for key, value in data.items():
            content.append(f"- {key}: {value}")
        content.append("")

    output_path.write_text("\n".join(content), encoding="utf-8")
    return output_path
