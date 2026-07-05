import pandas as pd


def drop_useless_columns(dataframe: pd.DataFrame, target_column: str | None = None) -> tuple[pd.DataFrame, list[str]]:
    engineered = dataframe.copy()
    dropped = []
    row_count = max(len(engineered), 1)

    for column in list(engineered.columns):
        if column == target_column:
            continue

        column_name = str(column).lower()
        unique_count = int(engineered[column].nunique(dropna=True))
        unique_ratio = unique_count / row_count

        if column_name in {"passengerid", "id", "name", "ticket"}:
            dropped.append(str(column))
            engineered = engineered.drop(columns=[column])
            continue

        if column_name.endswith("_id") or column_name.endswith("id"):
            dropped.append(str(column))
            engineered = engineered.drop(columns=[column])
            continue

        if pd.api.types.is_object_dtype(engineered[column]) and unique_ratio > 0.85:
            dropped.append(str(column))
            engineered = engineered.drop(columns=[column])

    return engineered, dropped


def select_features(dataframe: pd.DataFrame, target_column: str | None = None) -> tuple[pd.DataFrame, list[str]]:
    selected = dataframe.copy()
    dropped = []

    for column in list(selected.columns):
        if column == target_column:
            continue
        if selected[column].nunique(dropna=False) <= 1:
            dropped.append(str(column))
            selected = selected.drop(columns=[column])

    numeric_columns = [column for column in selected.select_dtypes(include=["number"]).columns if column != target_column]
    if len(numeric_columns) > 1:
        correlation = selected[numeric_columns].corr(numeric_only=True).abs()
        to_drop = set()
        for index, column in enumerate(correlation.columns):
            if column in to_drop:
                continue
            for other in correlation.columns[index + 1 :]:
                if other in to_drop:
                    continue
                value = correlation.loc[column, other]
                if pd.notna(value) and float(value) > 0.98:
                    to_drop.add(other)

        for column in sorted(to_drop):
            dropped.append(str(column))
            selected = selected.drop(columns=[column])

    return selected, dropped
