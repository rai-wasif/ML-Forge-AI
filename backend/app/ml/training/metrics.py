import math

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)


def classification_metrics(y_true, y_pred, probabilities=None) -> dict:
    labels = np.unique(y_true)
    average = "binary" if len(labels) == 2 else "weighted"
    roc_auc = None

    if probabilities is not None:
        try:
            if len(labels) == 2:
                roc_auc = roc_auc_score(y_true, probabilities[:, 1])
            else:
                roc_auc = roc_auc_score(y_true, probabilities, multi_class="ovo", average="weighted")
        except Exception:
            roc_auc = None

    return {
        "accuracy": clean_float(accuracy_score(y_true, y_pred)),
        "precision": clean_float(precision_score(y_true, y_pred, average=average, zero_division=0)),
        "recall": clean_float(recall_score(y_true, y_pred, average=average, zero_division=0)),
        "f1_score": clean_float(f1_score(y_true, y_pred, average=average, zero_division=0)),
        "roc_auc": clean_float(roc_auc),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }


def regression_metrics(y_true, y_pred) -> dict:
    mse = mean_squared_error(y_true, y_pred)
    return {
        "mae": clean_float(mean_absolute_error(y_true, y_pred)),
        "mse": clean_float(mse),
        "rmse": clean_float(math.sqrt(mse)),
        "r2": clean_float(r2_score(y_true, y_pred)),
    }


def clean_float(value):
    if value is None:
        return None
    value = float(value)
    if math.isnan(value) or math.isinf(value):
        return None
    return round(value, 6)
