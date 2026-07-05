import re

import pandas as pd


def create_domain_features(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    engineered = dataframe.copy()
    created = []

    if {"SibSp", "Parch"}.issubset(engineered.columns):
        engineered["FamilySize"] = engineered["SibSp"] + engineered["Parch"] + 1
        engineered["IsAlone"] = (engineered["FamilySize"] == 1).astype(int)
        created.extend(["FamilySize", "IsAlone"])

    if "Name" in engineered.columns:
        engineered["Title"] = engineered["Name"].astype(str).apply(extract_title)
        created.append("Title")

    return engineered, created


def extract_title(name: str) -> str:
    match = re.search(r",\s*([^\.]+)\.", name)
    if not match:
        return "Unknown"

    title = match.group(1).strip()
    common_titles = {"Mr", "Mrs", "Miss", "Master"}
    return title if title in common_titles else "Rare"
