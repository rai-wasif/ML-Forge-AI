import pandas as pd


def fill_missing_values(dataframe: pd.DataFrame, target_column: str | None = None) -> tuple[pd.DataFrame, dict]:
    cleaned = dataframe.copy()
    filled_columns = []

    for column in cleaned.columns:
        missing_count = int(cleaned[column].isna().sum())
        if missing_count == 0:
            continue

        if column == target_column:
            cleaned = cleaned[cleaned[column].notna()].reset_index(drop=True)
            filled_columns.append(
                {
                    "column": str(column),
                    "missing_before": missing_count,
                    "strategy": "drop_missing_target_rows",
                    "fill_value": None,
                }
            )
            continue

        if pd.api.types.is_numeric_dtype(cleaned[column]):
            fill_value = cleaned[column].median()
            strategy = "median"
            if pd.isna(fill_value):
                fill_value = cleaned[column].mean()
                strategy = "mean"
            if pd.isna(fill_value):
                fill_value = 0
                strategy = "zero"
        else:
            mode = cleaned[column].mode(dropna=True)
            fill_value = mode.iloc[0] if not mode.empty else "Unknown"
            strategy = "mode" if not mode.empty else "unknown"

        cleaned[column] = cleaned[column].fillna(fill_value)
        filled_columns.append(
            {
                "column": str(column),
                "missing_before": missing_count,
                "strategy": strategy,
                "fill_value": str(fill_value),
            }
        )

    return cleaned, {"filled_columns": filled_columns}
