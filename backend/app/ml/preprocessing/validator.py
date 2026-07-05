import re

import pandas as pd


POSITIVE_VALUE_HINTS = (
    "age",
    "amount",
    "balance",
    "count",
    "fare",
    "income",
    "price",
    "quantity",
    "salary",
    "sibsp",
    "parch",
)


def detect_target_column(dataframe: pd.DataFrame, requested_target: str | None = None) -> str | None:
    if requested_target and requested_target in dataframe.columns:
        return requested_target

    lower_lookup = {str(column).lower(): str(column) for column in dataframe.columns}
    for name in ("target", "label", "class", "survived", "outcome"):
        column = lower_lookup.get(name)
        if column and is_class_like(dataframe[column]):
            return column

    for column in dataframe.columns:
        if is_class_like(dataframe[column]):
            return str(column)

    return None


def is_class_like(series: pd.Series) -> bool:
    non_null = series.dropna()
    if non_null.empty:
        return False

    unique_count = int(non_null.nunique())
    return 2 <= unique_count <= min(20, max(2, int(len(non_null) * 0.2)))


def detect_and_fix_invalid_values(dataframe: pd.DataFrame, target_column: str | None = None) -> tuple[pd.DataFrame, dict]:
    cleaned = dataframe.copy()
    invalid_values = []

    for column in cleaned.columns:
        if column == target_column:
            continue

        column_name = str(column).lower()

        if pd.api.types.is_numeric_dtype(cleaned[column]) and any(hint in column_name for hint in POSITIVE_VALUE_HINTS):
            invalid_mask = cleaned[column] < 0
            invalid_count = int(invalid_mask.sum())
            if invalid_count:
                cleaned.loc[invalid_mask, column] = pd.NA
                invalid_values.append(
                    {
                        "column": str(column),
                        "invalid_count": invalid_count,
                        "rule": "negative_value_not_allowed",
                        "strategy": "set_to_missing",
                    }
                )
            continue

        if not pd.api.types.is_numeric_dtype(cleaned[column]):
            non_null = cleaned[column].dropna().astype(str)
            if non_null.empty or int(non_null.nunique()) > 50:
                continue

            numeric_like = non_null.str.fullmatch(re.compile(r"-?\d+(\.\d+)?"))
            numeric_like_count = int(numeric_like.sum())
            if 0 < numeric_like_count <= max(2, int(len(non_null) * 0.2)):
                invalid_tokens = set(non_null[numeric_like].tolist())
                cleaned[column] = cleaned[column].apply(
                    lambda value: "Unknown" if str(value) in invalid_tokens else value
                )
                invalid_values.append(
                    {
                        "column": str(column),
                        "invalid_count": numeric_like_count,
                        "rule": "numeric_token_in_categorical_column",
                        "strategy": "replace_with_unknown",
                    }
                )

    return cleaned, {"invalid_values": invalid_values}
