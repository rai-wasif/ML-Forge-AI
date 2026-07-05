from datetime import datetime

import pandas as pd

from app.ml.feature_engineering.categorical import categorical_columns
from app.ml.feature_engineering.datetime_features import create_datetime_features
from app.ml.feature_engineering.encoder import encode_features
from app.ml.feature_engineering.feature_creator import create_domain_features
from app.ml.feature_engineering.feature_selector import drop_useless_columns, select_features
from app.ml.feature_engineering.numerical import numerical_columns
from app.ml.feature_engineering.scaler import scale_features
from app.ml.preprocessing.pipeline import to_jsonable
from app.ml.preprocessing.validator import detect_target_column


def run_feature_pipeline(dataframe: pd.DataFrame, target_column: str | None = None) -> tuple[pd.DataFrame, dict]:
    original_columns = int(len(dataframe.columns))
    working = dataframe.copy()
    detected_target = detect_target_column(working, target_column)
    feature_types_before = detect_feature_types(working, detected_target)

    working, created_domain = create_domain_features(working)
    working, created_datetime = create_datetime_features(working, detected_target)
    working, dropped_useless = drop_useless_columns(working, detected_target)
    working, encoding_report = encode_features(working, detected_target)
    working, scaling_report = scale_features(working, detected_target)
    working, dropped_selected = select_features(working, detected_target)

    summary = {
        "original_columns": original_columns,
        "final_columns": int(len(working.columns)),
        "encoding_method": encoding_report["encoding_method"],
        "scaling_method": scaling_report["scaling_method"],
        "features_created": created_domain + created_datetime,
        "dropped_columns": dropped_useless + dropped_selected,
        "target_column": detected_target,
        "feature_types": feature_types_before,
        "encoding_report": encoding_report,
        "scaling_report": scaling_report,
        "selection_report": {
            "dropped_by_useless_rules": dropped_useless,
            "dropped_by_selection": dropped_selected,
        },
        "created_at": datetime.utcnow().isoformat(),
    }

    return working, to_jsonable(summary)


def detect_feature_types(dataframe: pd.DataFrame, target_column: str | None = None) -> dict:
    types = {
        "numerical": numerical_columns(dataframe, target_column),
        "categorical": categorical_columns(dataframe, target_column),
        "boolean": [],
        "datetime": [],
        "text": [],
        "target": target_column,
    }

    for column in dataframe.columns:
        if column == target_column:
            continue

        series = dataframe[column]
        if pd.api.types.is_bool_dtype(series):
            types["boolean"].append(str(column))
        elif pd.api.types.is_datetime64_any_dtype(series):
            types["datetime"].append(str(column))
        elif pd.api.types.is_object_dtype(series):
            avg_length = series.dropna().astype(str).str.len().mean()
            unique_ratio = series.nunique(dropna=True) / max(len(series), 1)
            if avg_length and avg_length > 30 and unique_ratio > 0.5:
                types["text"].append(str(column))

    return types
