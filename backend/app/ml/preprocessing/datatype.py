import pandas as pd


def correct_data_types(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    cleaned = dataframe.copy()
    changes = []

    for column in cleaned.columns:
        series = cleaned[column]

        if series.dtype != "object":
            continue

        non_null = series.dropna()
        if non_null.empty:
            continue

        numeric_series = pd.to_numeric(non_null, errors="coerce")
        numeric_ratio = float(numeric_series.notna().mean())
        if numeric_ratio >= 0.85:
            cleaned[column] = pd.to_numeric(series, errors="coerce")
            changes.append({"column": str(column), "from": "object", "to": str(cleaned[column].dtype)})
            continue

        column_name = str(column).lower()
        if "date" in column_name or "time" in column_name:
            datetime_series = pd.to_datetime(series, errors="coerce")
            if float(datetime_series.notna().mean()) >= 0.7:
                cleaned[column] = datetime_series
                changes.append({"column": str(column), "from": "object", "to": "datetime64"})

    return cleaned, changes
