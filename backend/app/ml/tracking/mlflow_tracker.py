from pathlib import Path

from app.core.config import get_settings


def log_training_run(
    project_name: str,
    dataset_name: str,
    summary: dict,
    artifact_paths: list[str | Path],
) -> dict:
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
    except Exception as exc:
        return {"status": "unavailable", "error": f"MLflow import failed: {exc}"}

    settings = get_settings()
    experiment_name = f"MLForge-{safe_name(project_name)}"
    run_id = None
    artifact_uri = None

    try:
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        client = MlflowClient(tracking_uri=settings.mlflow_tracking_uri)
        experiment = client.get_experiment_by_name(experiment_name)
        experiment_id = (
            experiment.experiment_id
            if experiment is not None
            else client.create_experiment(experiment_name)
        )
        run = client.create_run(
            experiment_id=experiment_id,
            run_name=f"{safe_name(dataset_name)}-{safe_name(summary['best_model'])}",
        )
        run_id = run.info.run_id
        artifact_uri = run.info.artifact_uri

        params = {
            "project": project_name,
            "dataset": dataset_name,
            "problem_type": summary["problem_type"],
            "target_column": summary["target_column"],
            "best_model": summary["best_model"],
            "selected_models": ",".join(summary.get("selected_models", [])),
        }
        for key, value in params.items():
            client.log_param(run_id, key, str(value)[:500])

        client.log_metric(run_id, "training_time", float(summary.get("training_time", 0)))
        for key, value in flatten_metrics(summary.get("best_metrics", {})).items():
            if isinstance(value, (int, float)):
                client.log_metric(run_id, f"best_{safe_metric_name(key)}", float(value))

        for result in summary.get("model_results", []):
            model_key = safe_metric_name(safe_name(result.get("model", "model")).lower())
            if isinstance(result.get("score"), (int, float)):
                client.log_metric(run_id, f"{model_key}_score", float(result["score"]))

        for path in artifact_paths:
            artifact_path = Path(path)
            if artifact_path.exists():
                client.log_artifact(run_id, str(artifact_path))

        client.set_terminated(run_id, status="FINISHED")
        finished_run = client.get_run(run_id)
        artifact_uri = finished_run.info.artifact_uri
        return {
            "status": "logged",
            "tracking_uri": settings.mlflow_tracking_uri,
            "experiment_name": experiment_name,
            "run_id": run_id,
            "artifact_uri": artifact_uri,
        }
    except Exception as exc:
        if run_id and is_console_encoding_error(exc):
            try:
                MlflowClient(tracking_uri=settings.mlflow_tracking_uri).set_terminated(run_id, status="FINISHED")
            except Exception:
                pass
            return {
                "status": "logged",
                "tracking_uri": settings.mlflow_tracking_uri,
                "experiment_name": experiment_name,
                "run_id": run_id,
                "artifact_uri": artifact_uri,
                "warning": str(exc),
            }

        if run_id:
            try:
                MlflowClient(tracking_uri=settings.mlflow_tracking_uri).set_terminated(run_id, status="FAILED")
            except Exception:
                pass
        return {
            "status": "failed",
            "tracking_uri": settings.mlflow_tracking_uri,
            "experiment_name": experiment_name,
            "error": str(exc),
        }


def flatten_metrics(metrics: dict, prefix: str = "") -> dict:
    output = {}
    for key, value in metrics.items():
        metric_key = f"{prefix}_{key}" if prefix else str(key)
        if isinstance(value, dict):
            output.update(flatten_metrics(value, metric_key))
        elif isinstance(value, list):
            continue
        else:
            output[metric_key] = value
    return output


def safe_name(value: str) -> str:
    return "".join(character if character.isalnum() or character in "-_" else "-" for character in str(value)).strip("-") or "project"


def safe_metric_name(value: str) -> str:
    return "".join(character if character.isalnum() or character in "_-." else "_" for character in str(value))


def is_console_encoding_error(exc: Exception) -> bool:
    message = str(exc)
    return isinstance(exc, UnicodeEncodeError) or "charmap" in message or "codec can't encode" in message
