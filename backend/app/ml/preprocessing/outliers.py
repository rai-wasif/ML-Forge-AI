import pandas as pd


def clip_outliers_iqr(dataframe: pd.DataFrame, target_column: str | None = None) -> tuple[pd.DataFrame, dict]:
    cleaned = dataframe.copy()
    handled_columns = []
    total_outliers = 0

    for column in cleaned.select_dtypes(include=["number"]).columns:
        if column == target_column:
            continue

        column_name = str(column).lower()
        if column_name == "id" or column_name.endswith("_id") or column_name.endswith("id"):
            continue

        series = cleaned[column].dropna()
        if series.empty or int(series.nunique()) <= 10:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outlier_mask = (cleaned[column] < lower_bound) | (cleaned[column] > upper_bound)
        outlier_count = int(outlier_mask.sum())

        if outlier_count == 0:
            continue

        cleaned[column] = cleaned[column].clip(lower=lower_bound, upper=upper_bound)
        total_outliers += outlier_count
        handled_columns.append(
            {
                "column": str(column),
                "outlier_count": outlier_count,
                "strategy": "iqr_clip",
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
            }
        )

    return cleaned, {
        "total_outliers_handled": total_outliers,
        "columns": handled_columns,
    }
