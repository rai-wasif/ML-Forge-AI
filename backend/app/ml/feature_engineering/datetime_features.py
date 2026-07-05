import pandas as pd


def create_datetime_features(dataframe: pd.DataFrame, target_column: str | None = None) -> tuple[pd.DataFrame, list[str]]:
    engineered = dataframe.copy()
    created = []

    for column in list(engineered.columns):
        if column == target_column:
            continue

        if not pd.api.types.is_datetime64_any_dtype(engineered[column]):
            continue

        engineered[f"{column}_year"] = engineered[column].dt.year
        engineered[f"{column}_month"] = engineered[column].dt.month
        engineered[f"{column}_day"] = engineered[column].dt.day
        engineered[f"{column}_dayofweek"] = engineered[column].dt.dayofweek
        created.extend(
            [
                f"{column}_year",
                f"{column}_month",
                f"{column}_day",
                f"{column}_dayofweek",
            ]
        )
        engineered = engineered.drop(columns=[column])

    return engineered, created
