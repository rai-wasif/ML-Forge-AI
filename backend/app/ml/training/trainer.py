import time

import optuna
from catboost import CatBoostClassifier, CatBoostRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier, XGBRegressor

from app.ml.training.evaluator import evaluate_model, score_for_selection
from app.ml.training.model_selector import RANDOM_STATE, select_models


optuna.logging.set_verbosity(optuna.logging.WARNING)
OPTIMIZABLE_MODELS = {
    "Random Forest",
    "Random Forest Regressor",
    "XGBoost",
    "XGBoost Regressor",
    "LightGBM",
    "LightGBM Regressor",
    "CatBoost",
    "CatBoost Regressor",
}


def train_models(features, target, problem_type: str) -> dict:
    stratify = target if problem_type == "classification" and min_class_count(target) >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    candidates = select_models(problem_type)
    results = []
    fitted_models = {}

    for name, model in candidates.items():
        result = fit_and_evaluate(name, model, x_train, y_train, x_test, y_test, problem_type)
        results.append(result)
        fitted_models[name] = result["model_object"]

    ranked = sorted(results, key=lambda item: item["score"], reverse=True)
    optimized_results = []
    optimizable_ranked = [result for result in ranked if result["model"] in OPTIMIZABLE_MODELS]
    for result in optimizable_ranked[:2]:
        optimized = optimize_model(result["model"], x_train, y_train, x_test, y_test, problem_type)
        if optimized:
            optimized_results.append(optimized)
            fitted_models[optimized["model"]] = optimized["model_object"]

    all_results = results + optimized_results
    best = sorted(all_results, key=lambda item: item["score"], reverse=True)[0]

    public_results = [
        {
            "model": item["model"],
            "metrics": item["metrics"],
            "score": item["score"],
            "training_time": item["training_time"],
            "inference_time": item["inference_time"],
            "optimized": item.get("optimized", False),
        }
        for item in sorted(all_results, key=lambda item: item["score"], reverse=True)
    ]

    return {
        "selected_models": list(candidates.keys()),
        "optimized_models": [item["model"] for item in optimized_results],
        "model_results": public_results,
        "best_model_name": best["model"],
        "best_model": best["model_object"],
        "best_metrics": best["metrics"],
    }


def fit_and_evaluate(name, model, x_train, y_train, x_test, y_test, problem_type: str) -> dict:
    start = time.perf_counter()
    model.fit(x_train, y_train)
    training_time = time.perf_counter() - start
    metrics, inference_time = evaluate_model(model, x_test, y_test, problem_type)

    return {
        "model": name,
        "model_object": model,
        "metrics": metrics,
        "score": score_for_selection(metrics, problem_type),
        "training_time": round(training_time, 6),
        "inference_time": round(inference_time, 6),
    }


def optimize_model(name, x_train, y_train, x_test, y_test, problem_type: str) -> dict | None:
    def objective(trial):
        model = build_trial_model(name, trial, problem_type)
        if model is None:
            raise optuna.exceptions.TrialPruned()
        result = fit_and_evaluate(name, model, x_train, y_train, x_test, y_test, problem_type)
        return result["score"]

    try:
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=2, show_progress_bar=False)
        model = build_trial_model(name, study.best_trial, problem_type)
        if model is None:
            return None
        result = fit_and_evaluate(f"{name} Optimized", model, x_train, y_train, x_test, y_test, problem_type)
        result["optimized"] = True
        return result
    except Exception:
        return None


def build_trial_model(name, trial, problem_type: str):
    if name in {"Random Forest", "Random Forest Regressor"}:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 60, 140),
            "max_depth": trial.suggest_int("max_depth", 3, 12),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 8),
            "random_state": RANDOM_STATE,
            "n_jobs": -1,
        }
        return RandomForestClassifier(**params) if problem_type == "classification" else RandomForestRegressor(**params)

    if name in {"XGBoost", "XGBoost Regressor"}:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 40, 100),
            "max_depth": trial.suggest_int("max_depth", 2, 5),
            "learning_rate": trial.suggest_float("learning_rate", 0.03, 0.2),
            "subsample": trial.suggest_float("subsample", 0.7, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.7, 1.0),
            "random_state": RANDOM_STATE,
            "n_jobs": 1,
            "verbosity": 0,
        }
        if problem_type == "classification":
            return XGBClassifier(**params, eval_metric="logloss")
        return XGBRegressor(**params)

    if name in {"LightGBM", "LightGBM Regressor"}:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 40, 100),
            "max_depth": trial.suggest_int("max_depth", 2, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.03, 0.2),
            "random_state": RANDOM_STATE,
            "verbosity": -1,
        }
        return LGBMClassifier(**params) if problem_type == "classification" else LGBMRegressor(**params)

    if name in {"CatBoost", "CatBoost Regressor"}:
        params = {
            "iterations": trial.suggest_int("iterations", 40, 100),
            "depth": trial.suggest_int("depth", 3, 6),
            "learning_rate": trial.suggest_float("learning_rate", 0.03, 0.2),
            "random_state": RANDOM_STATE,
            "verbose": False,
            "allow_writing_files": False,
        }
        return CatBoostClassifier(**params) if problem_type == "classification" else CatBoostRegressor(**params)

    return None


def min_class_count(target) -> int:
    counts = {}
    for value in target:
        counts[value] = counts.get(value, 0) + 1
    return min(counts.values()) if counts else 0
