import time

from app.ml.training.metrics import classification_metrics, regression_metrics


def evaluate_model(model, x_test, y_test, problem_type: str) -> tuple[dict, float]:
    start = time.perf_counter()
    predictions = model.predict(x_test)
    inference_time = time.perf_counter() - start

    if problem_type == "classification":
        probabilities = model.predict_proba(x_test) if hasattr(model, "predict_proba") else None
        return classification_metrics(y_test, predictions, probabilities), inference_time

    return regression_metrics(y_test, predictions), inference_time


def score_for_selection(metrics: dict, problem_type: str) -> float:
    if problem_type == "classification":
        return metrics.get("roc_auc") or metrics.get("f1_score") or metrics.get("accuracy") or 0.0

    rmse = metrics.get("rmse")
    return -float(rmse) if rmse is not None else -1e12
