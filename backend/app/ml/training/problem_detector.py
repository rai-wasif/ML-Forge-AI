import pandas as pd
from sklearn.preprocessing import LabelEncoder


def detect_problem_type(target: pd.Series) -> str:
    non_null = target.dropna()

    if not pd.api.types.is_numeric_dtype(non_null):
        return "classification"

    unique_count = int(non_null.nunique())
    unique_ratio = unique_count / max(len(non_null), 1)

    if unique_count <= 20 and unique_ratio <= 0.2:
        return "classification"

    return "regression"


def prepare_target(target: pd.Series, problem_type: str):
    if problem_type == "classification":
        encoder = LabelEncoder()
        encoded = encoder.fit_transform(target.astype(str))
        return encoded, encoder

    return target.astype(float), None
