import math
from datetime import date, datetime

import numpy as np
import pandas as pd

from app.ml.preprocessing.datatype import correct_data_types
from app.ml.preprocessing.duplicates import remove_duplicates
from app.ml.preprocessing.missing_values import fill_missing_values
from app.ml.preprocessing.outliers import clip_outliers_iqr
from app.ml.preprocessing.validator import detect_and_fix_invalid_values, detect_target_column


def run_cleaning_pipeline(dataframe: pd.DataFrame, target_column: str | None = None) -> tuple[pd.DataFrame, dict]:
    original_rows, original_columns = dataframe.shape
    missing_before = int(dataframe.isna().sum().sum())

    cleaned, datatype_report = correct_data_types(dataframe)
    detected_target = detect_target_column(cleaned, target_column)
    cleaned, invalid_report = detect_and_fix_invalid_values(cleaned, detected_target)
    cleaned, duplicate_report = remove_duplicates(cleaned)
    cleaned, missing_report = fill_missing_values(cleaned, detected_target)
    cleaned, outlier_report = clip_outliers_iqr(cleaned, detected_target)

    missing_after = int(cleaned.isna().sum().sum())
    final_rows, final_columns = cleaned.shape

    summary = {
        "target_column": detected_target,
        "original_rows": int(original_rows),
        "final_rows": int(final_rows),
        "original_columns": int(original_columns),
        "final_columns": int(final_columns),
        "missing_values_before": missing_before,
        "missing_values_after": missing_after,
        "duplicates_removed": duplicate_report["duplicates_removed"],
        "outliers_handled": outlier_report["total_outliers_handled"],
        "datatype_changes": datatype_report,
        "invalid_value_report": invalid_report,
        "duplicate_report": duplicate_report,
        "missing_value_report": missing_report,
        "outlier_report": outlier_report,
        "filled_columns": [item["column"] for item in missing_report["filled_columns"]],
        "created_at": datetime.utcnow().isoformat(),
    }

    return cleaned, to_jsonable(summary)


def to_jsonable(value):
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(item) for item in value]

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        value = float(value)

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return round(value, 6)

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    return value
