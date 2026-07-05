import time

import pandas as pd

from app.ml.preprocessing.pipeline import to_jsonable
from app.ml.training.model_saver import save_training_artifacts
from app.ml.training.problem_detector import detect_problem_type, prepare_target
from app.ml.training.trainer import train_models


def run_training_pipeline(
    feature_dataset_path,
    target_column: str,
    output_dir,
    feature_summary: dict,
) -> dict:
    started = time.perf_counter()
    dataframe = pd.read_parquet(feature_dataset_path)

    if target_column not in dataframe.columns:
        raise ValueError(f"Target column '{target_column}' was not found in the feature dataset.")

    dataframe = dataframe.dropna(subset=[target_column]).reset_index(drop=True)
    features = dataframe.drop(columns=[target_column])
    features = features.apply(pd.to_numeric, errors="coerce").fillna(0)
    raw_target = dataframe[target_column]

    problem_type = detect_problem_type(raw_target)
    target, label_encoder = prepare_target(raw_target, problem_type)
    training_result = train_models(features, target, problem_type)
    training_time = time.perf_counter() - started

    summary = {
        "problem_type": problem_type,
        "target_column": target_column,
        "selected_models": training_result["selected_models"],
        "optimized_models": training_result["optimized_models"],
        "best_model": training_result["best_model_name"],
        "best_metrics": training_result["best_metrics"],
        "metrics": {
            "best": training_result["best_metrics"],
            "comparison": training_result["model_results"],
        },
        "model_results": training_result["model_results"],
        "training_time": round(training_time, 6),
    }

    artifacts = save_training_artifacts(
        output_dir,
        training_result["best_model"],
        label_encoder,
        feature_summary,
        summary,
    )
    summary["artifacts"] = artifacts

    return to_jsonable(summary)
