import pandas as pd


def categorical_columns(dataframe: pd.DataFrame, target_column: str | None = None) -> list[str]:
    columns = []
    for column in dataframe.columns:
        if column == target_column:
            continue
        if pd.api.types.is_object_dtype(dataframe[column]) or pd.api.types.is_categorical_dtype(dataframe[column]):
            columns.append(str(column))
    return columns
