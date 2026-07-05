import json
from pathlib import Path

import joblib
import matplotlib
import numpy as np
import pandas as pd

from app.ml.preprocessing.pipeline import to_jsonable


matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def generate_shap_report(
    model_path: str | Path,
    feature_dataset_path: str | Path,
    target_column: str,
    output_dir: str | Path,
    max_rows: int = 200,
) -> dict:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary_path = output_path / "shap_summary.png"
    importance_path = output_path / "shap_feature_importance.png"
    json_path = output_path / "shap_summary.json"

    dataframe = pd.read_parquet(feature_dataset_path)
    if target_column not in dataframe.columns:
        raise ValueError(f"Target column '{target_column}' was not found in feature dataset.")

    features = dataframe.drop(columns=[target_column])
    features = features.apply(pd.to_numeric, errors="coerce").fillna(0)
    sample = features.sample(min(max_rows, len(features)), random_state=42) if len(features) > max_rows else features
    model = joblib.load(model_path)

    result = compute_shap_values(model, sample)
    method = result["method"]
    values = result["values"]
    importances = feature_importance(values, sample.columns)

    create_importance_plot(importances, importance_path)
    if method == "shap":
        create_shap_summary_plot(result["raw_values"], sample, summary_path)
    else:
        create_importance_plot(importances, summary_path, title="Model Feature Importance")

    payload = {
        "status": "completed",
        "method": method,
        "sample_rows": int(len(sample)),
        "top_features": importances[:15],
        "summary_path": str(summary_path),
        "importance_path": str(importance_path),
        "summary_url": report_url(summary_path),
        "importance_url": report_url(importance_path),
        "json_path": str(json_path),
    }

    json_path.write_text(json.dumps(to_jsonable(payload), indent=2), encoding="utf-8")
    return to_jsonable(payload)


def compute_shap_values(model, sample: pd.DataFrame) -> dict:
    try:
        import shap

        explainer = shap.Explainer(model, sample)
        explanation = explainer(sample)
        values = np.asarray(explanation.values)
        return {"method": "shap", "values": values, "raw_values": explanation}
    except Exception:
        values = fallback_importance_values(model, sample)
        return {"method": "model_importance_fallback", "values": values, "raw_values": None}


def fallback_importance_values(model, sample: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "feature_importances_"):
        values = np.asarray(model.feature_importances_, dtype=float)
    elif hasattr(model, "coef_"):
        values = np.abs(np.asarray(model.coef_, dtype=float))
        if values.ndim > 1:
            values = values.mean(axis=0)
    else:
        values = sample.var(numeric_only=True).to_numpy(dtype=float)

    if values.ndim == 1:
        return np.tile(values, (len(sample), 1))

    return values


def feature_importance(values: np.ndarray, columns) -> list[dict]:
    array = np.asarray(values, dtype=float)
    if array.ndim == 3:
        array = np.abs(array).mean(axis=2)
    elif array.ndim == 1:
        array = array.reshape(1, -1)

    scores = np.abs(array).mean(axis=0)
    pairs = sorted(zip(columns, scores), key=lambda item: item[1], reverse=True)
    return [{"feature": str(feature), "importance": round(float(score), 6)} for feature, score in pairs]


def create_shap_summary_plot(explanation, sample: pd.DataFrame, path: Path) -> None:
    import shap

    plt.figure()
    shap.summary_plot(explanation, sample, show=False, max_display=15)
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight")
    plt.close()


def create_importance_plot(importances: list[dict], path: Path, title: str = "SHAP Feature Importance") -> None:
    top = list(reversed(importances[:15]))
    labels = [item["feature"] for item in top]
    values = [item["importance"] for item in top]

    fig, axis = plt.subplots(figsize=(9, max(4, len(top) * 0.35)))
    axis.barh(labels, values, color="#0f766e")
    axis.set_title(title)
    axis.set_xlabel("Mean absolute impact")
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def report_url(path: Path) -> str:
    reports_root = Path(__file__).resolve().parents[2] / "storage" / "reports"
    relative = path.relative_to(reports_root).as_posix()
    return f"/reports/{relative}"
