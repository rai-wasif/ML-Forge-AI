import pandas as pd


def remove_duplicates(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    duplicate_count = int(dataframe.duplicated().sum())
    cleaned = dataframe.drop_duplicates().reset_index(drop=True)

    return cleaned, {
        "duplicates_found": duplicate_count,
        "duplicates_removed": duplicate_count,
    }
