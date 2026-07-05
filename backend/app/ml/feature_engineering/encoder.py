import pandas as pd


def encode_features(dataframe: pd.DataFrame, target_column: str | None = None) -> tuple[pd.DataFrame, dict]:
    encoded = dataframe.copy()
    one_hot_columns = []
    label_encoded_columns = []

    for column in list(encoded.columns):
        if column == target_column:
            continue

        if pd.api.types.is_bool_dtype(encoded[column]):
            encoded[column] = encoded[column].astype(int)
            continue

        if not pd.api.types.is_object_dtype(encoded[column]) and not pd.api.types.is_categorical_dtype(encoded[column]):
            continue

        unique_count = int(encoded[column].nunique(dropna=True))

        if unique_count <= 10:
            dummies = pd.get_dummies(encoded[column], prefix=str(column), dummy_na=False, dtype=int)
            encoded = pd.concat([encoded.drop(columns=[column]), dummies], axis=1)
            one_hot_columns.append(str(column))
        else:
            codes, _ = pd.factorize(encoded[column].astype(str), sort=True)
            encoded[column] = codes
            label_encoded_columns.append(str(column))

    methods = []
    if one_hot_columns:
        methods.append("one_hot")
    if label_encoded_columns:
        methods.append("label")

    return encoded, {
        "encoding_method": "+".join(methods) if methods else "none",
        "one_hot_columns": one_hot_columns,
        "label_encoded_columns": label_encoded_columns,
    }
