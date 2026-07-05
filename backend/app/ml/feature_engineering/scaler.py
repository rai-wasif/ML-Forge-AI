import pandas as pd


def scale_features(dataframe: pd.DataFrame, target_column: str | None = None) -> tuple[pd.DataFrame, dict]:
    scaled = dataframe.copy()
    scaled_columns = []

    for column in scaled.select_dtypes(include=["number"]).columns:
        if column == target_column:
            continue

        series = scaled[column]
        unique_count = int(series.nunique(dropna=True))
        if unique_count <= 2:
            continue

        mean = series.mean()
        std = series.std()
        if pd.isna(std) or std == 0:
            continue

        scaled[column] = (series - mean) / std
        scaled_columns.append(str(column))

    return scaled, {
        "scaling_method": "standard" if scaled_columns else "none",
        "scaled_columns": scaled_columns,
    }
