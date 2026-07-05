import pandas as pd


def numerical_columns(dataframe: pd.DataFrame, target_column: str | None = None) -> list[str]:
    columns = []
    for column in dataframe.select_dtypes(include=["number"]).columns:
        if column != target_column:
            columns.append(str(column))
    return columns
