from crewai.tools import tool

from app.database.session import SessionLocal
from app.services import cleaning_service, eda_service, feature_service, training_service


@tool("run_eda")
def run_eda_tool(dataset_id: int) -> str:
    """Run EDA for a dataset and return a short summary."""
    db = SessionLocal()
    try:
        report = eda_service.analyze_dataset(db, int(dataset_id))
        overview = report.report_data["dataset_overview"]
        return (
            f"EDA completed for dataset {dataset_id}: "
            f"{overview['rows']} rows, {overview['columns']} columns, "
            f"{overview['total_missing_values']} missing values."
        )
    finally:
        db.close()


@tool("run_cleaning")
def run_cleaning_tool(dataset_id: int) -> str:
    """Run the cleaning pipeline for a dataset and return a short summary."""
    db = SessionLocal()
    try:
        report = cleaning_service.run_cleaning(db, int(dataset_id))
        return (
            f"Cleaning completed for dataset {dataset_id}: "
            f"missing {report.missing_values_before}->{report.missing_values_after}, "
            f"duplicates removed {report.duplicates_removed}, "
            f"outliers handled {report.outliers_handled}."
        )
    finally:
        db.close()


@tool("generate_features")
def generate_features_tool(dataset_id: int) -> str:
    """Generate ML features for a dataset and return a short summary."""
    db = SessionLocal()
    try:
        report = feature_service.generate_features(db, int(dataset_id))
        return (
            f"Features generated for dataset {dataset_id}: "
            f"{report.original_columns}->{report.final_columns} columns, "
            f"encoding={report.encoding_method}, scaling={report.scaling_method}."
        )
    finally:
        db.close()


@tool("train_model")
def train_model_tool(dataset_id: int) -> str:
    """Train candidate models for a dataset and return a short summary."""
    db = SessionLocal()
    try:
        report = training_service.train_dataset(db, int(dataset_id))
        return (
            f"Training completed for dataset {dataset_id}: "
            f"problem={report.problem_type}, best_model={report.best_model}."
        )
    finally:
        db.close()


def ml_pipeline_tools():
    return [run_eda_tool, run_cleaning_tool, generate_features_tool, train_model_tool]
