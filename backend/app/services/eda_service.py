import html
import json
import math
from datetime import date, datetime
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.dataset import Dataset
from app.models.eda_report import EDAReport
from app.services.dataset_service import read_dataframe


matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


REPORTS_ROOT = Path(__file__).resolve().parents[1] / "storage" / "reports" / "eda"


def analyze_dataset(db: Session, dataset_id: int, target_column: str | None = None) -> EDAReport:
    dataset = get_dataset_or_404(db, dataset_id)
    dataset_path = Path(dataset.file_path or "")

    if not dataset_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset file was not found on disk.",
        )

    extension = f".{dataset.file_type}" if dataset.file_type else dataset_path.suffix.lower()
    dataframe = read_dataframe(dataset_path, extension)
    report_dir = REPORTS_ROOT / f"project_{dataset.project_id:03d}" / f"dataset_{dataset.id:03d}"
    report_dir.mkdir(parents=True, exist_ok=True)

    selected_target = infer_target_column(dataframe, target_column)
    report_data = build_eda_report_data(dataset, dataframe, selected_target)
    visualizations = generate_visualizations(dataframe, report_dir, selected_target)
    report_data["visualizations"] = visualizations

    report_data = to_jsonable(report_data)
    json_path = report_dir / "eda_report.json"
    html_path = report_dir / "eda_report.html"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=2, allow_nan=False)

    html_path.write_text(render_html_report(report_data), encoding="utf-8")

    report = EDAReport(
        project_id=dataset.project_id,
        dataset_id=dataset.id,
        report_path=str(html_path),
        report_json_path=str(json_path),
        report_data=report_data,
        visualizations=visualizations,
    )

    db.add(report)
    db.flush()
    log_activity(db, dataset.project_id, "EDA Completed", f"EDA report generated for '{dataset.name}'.")
    db.commit()
    db.refresh(report)
    return report


def get_latest_report(db: Session, dataset_id: int) -> EDAReport | None:
    return db.scalars(
        select(EDAReport)
        .where(EDAReport.dataset_id == dataset_id)
        .order_by(EDAReport.created_at.desc())
    ).first()


def get_report_or_404(db: Session, report_id: int) -> EDAReport:
    report = db.get(EDAReport, report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="EDA report not found.",
        )
    return report


def get_dataset_or_404(db: Session, dataset_id: int) -> Dataset:
    dataset = db.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )
    return dataset


def build_eda_report_data(dataset: Dataset, dataframe: pd.DataFrame, target_column: str | None) -> dict:
    missing_by_column = dataframe.isna().sum()
    duplicate_rows = int(dataframe.duplicated().sum())
    row_count = int(len(dataframe))

    return {
        "dataset_overview": {
            "dataset_id": dataset.id,
            "dataset_name": dataset.name,
            "rows": row_count,
            "columns": int(len(dataframe.columns)),
            "total_missing_values": int(missing_by_column.sum()),
            "duplicate_rows": duplicate_rows,
            "duplicate_percentage": percentage(duplicate_rows, row_count),
            "memory_usage_bytes": int(dataframe.memory_usage(deep=True).sum()),
            "file_size_bytes": dataset.file_size_bytes,
        },
        "column_analysis": build_column_analysis(dataframe, missing_by_column),
        "numerical_statistics": build_numerical_statistics(dataframe),
        "categorical_analysis": build_categorical_analysis(dataframe),
        "missing_value_analysis": build_missing_value_analysis(dataframe, missing_by_column),
        "duplicate_analysis": {
            "duplicate_rows": duplicate_rows,
            "duplicate_percentage": percentage(duplicate_rows, row_count),
        },
        "correlation_analysis": build_correlation_analysis(dataframe),
        "outlier_detection": build_outlier_detection(dataframe),
        "class_balance": build_class_balance(dataframe, target_column),
        "generated_at": datetime.utcnow().isoformat(),
    }


def build_column_analysis(dataframe: pd.DataFrame, missing_by_column: pd.Series) -> list[dict]:
    rows = max(len(dataframe), 1)
    columns = []

    for column in dataframe.columns:
        series = dataframe[column]
        examples = list(series.dropna().unique()[:5])
        columns.append(
            {
                "name": str(column),
                "data_type": str(series.dtype),
                "unique_values": int(series.nunique(dropna=True)),
                "missing_percentage": percentage(int(missing_by_column[column]), rows),
                "example_values": examples,
            }
        )

    return columns


def build_numerical_statistics(dataframe: pd.DataFrame) -> list[dict]:
    stats = []

    for column in numeric_columns(dataframe):
        series = pd.to_numeric(dataframe[column], errors="coerce").dropna()
        if series.empty:
            continue

        mode = series.mode(dropna=True)
        quartiles = series.quantile([0.25, 0.5, 0.75])

        stats.append(
            {
                "column": str(column),
                "mean": clean_number(series.mean()),
                "median": clean_number(series.median()),
                "mode": clean_number(mode.iloc[0]) if not mode.empty else None,
                "minimum": clean_number(series.min()),
                "maximum": clean_number(series.max()),
                "standard_deviation": clean_number(series.std()),
                "variance": clean_number(series.var()),
                "quartiles": {
                    "q1": clean_number(quartiles.loc[0.25]),
                    "q2": clean_number(quartiles.loc[0.5]),
                    "q3": clean_number(quartiles.loc[0.75]),
                },
            }
        )

    return stats


def build_categorical_analysis(dataframe: pd.DataFrame) -> list[dict]:
    analysis = []

    for column in categorical_columns(dataframe):
        series = dataframe[column]
        non_null_counts = series.dropna().astype(str).value_counts()
        frequency_counts = [
            {"value": str(value), "count": int(count)}
            for value, count in series.fillna("<missing>").astype(str).value_counts().head(10).items()
        ]

        analysis.append(
            {
                "column": str(column),
                "frequency_counts": frequency_counts,
                "most_common_category": str(non_null_counts.index[0]) if not non_null_counts.empty else None,
                "least_common_category": str(non_null_counts.index[-1]) if not non_null_counts.empty else None,
                "cardinality": int(series.nunique(dropna=True)),
                "missing_count": int(series.isna().sum()),
            }
        )

    return analysis


def build_missing_value_analysis(dataframe: pd.DataFrame, missing_by_column: pd.Series) -> list[dict]:
    rows = max(len(dataframe), 1)
    missing_rows = []

    for column, count in missing_by_column.sort_values(ascending=False).items():
        if int(count) == 0:
            continue
        missing_rows.append(
            {
                "column": str(column),
                "missing_count": int(count),
                "missing_percentage": percentage(int(count), rows),
            }
        )

    return missing_rows


def build_correlation_analysis(dataframe: pd.DataFrame) -> dict:
    cols = numeric_columns(dataframe)
    if len(cols) < 2:
        return {"matrix": {}, "highly_correlated_features": []}

    correlation = dataframe[cols].corr(numeric_only=True).round(4)
    pairs = []

    for i, left in enumerate(correlation.columns):
        for right in correlation.columns[i + 1 :]:
            value = correlation.loc[left, right]
            if pd.notna(value) and abs(float(value)) >= 0.7:
                pairs.append(
                    {
                        "feature_1": str(left),
                        "feature_2": str(right),
                        "correlation": clean_number(value),
                    }
                )

    return {
        "matrix": correlation.to_dict(),
        "highly_correlated_features": pairs,
    }


def build_outlier_detection(dataframe: pd.DataFrame) -> list[dict]:
    outliers = []

    for column in numeric_columns(dataframe):
        series = pd.to_numeric(dataframe[column], errors="coerce").dropna()
        if series.empty:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        count = int(((series < lower_bound) | (series > upper_bound)).sum())

        outliers.append(
            {
                "column": str(column),
                "outlier_count": count,
                "outlier_percentage": percentage(count, len(series)),
                "lower_bound": clean_number(lower_bound),
                "upper_bound": clean_number(upper_bound),
            }
        )

    return outliers


def build_class_balance(dataframe: pd.DataFrame, target_column: str | None) -> dict | None:
    if not target_column or target_column not in dataframe.columns:
        return None

    series = dataframe[target_column]
    counts = series.fillna("<missing>").astype(str).value_counts()
    total = max(int(counts.sum()), 1)

    return {
        "target_column": str(target_column),
        "classes": [
            {
                "class": str(label),
                "count": int(count),
                "percentage": percentage(int(count), total),
            }
            for label, count in counts.items()
        ],
    }


def generate_visualizations(dataframe: pd.DataFrame, report_dir: Path, target_column: str | None) -> list[dict]:
    visualizations = []

    for plotter in (
        create_histogram,
        create_box_plot,
        create_correlation_heatmap,
        create_missing_value_matrix,
        create_class_distribution,
        create_scatter_plot,
    ):
        visualization = plotter(dataframe, report_dir, target_column)
        if visualization:
            visualizations.append(visualization)

    return visualizations


def create_histogram(dataframe: pd.DataFrame, report_dir: Path, target_column: str | None = None) -> dict | None:
    cols = numeric_columns(dataframe)[:6]
    if not cols:
        return None

    fig, axes = plt.subplots(len(cols), 1, figsize=(9, max(3, len(cols) * 2.4)))
    axes = np.atleast_1d(axes)

    for axis, column in zip(axes, cols):
        series = pd.to_numeric(dataframe[column], errors="coerce").dropna()
        axis.hist(series, bins=30, color="#0f766e", edgecolor="#ffffff")
        axis.set_title(f"Histogram: {column}")
        axis.set_ylabel("Count")

    path = save_figure(fig, report_dir / "histogram.png")
    return visualization_payload("Histogram", "histogram", path)


def create_box_plot(dataframe: pd.DataFrame, report_dir: Path, target_column: str | None = None) -> dict | None:
    cols = numeric_columns(dataframe)[:8]
    if not cols:
        return None

    fig, axis = plt.subplots(figsize=(10, 5))
    dataframe[cols].plot(kind="box", ax=axis, rot=30)
    axis.set_title("Box Plot")
    axis.set_ylabel("Value")
    path = save_figure(fig, report_dir / "box_plot.png")
    return visualization_payload("Box Plot", "box_plot", path)


def create_correlation_heatmap(dataframe: pd.DataFrame, report_dir: Path, target_column: str | None = None) -> dict | None:
    cols = numeric_columns(dataframe)
    if len(cols) < 2:
        return None

    cols = cols[:12]
    correlation = dataframe[cols].corr(numeric_only=True)
    fig, axis = plt.subplots(figsize=(9, 7))
    image = axis.imshow(correlation, cmap="viridis", vmin=-1, vmax=1)
    axis.set_title("Correlation Heatmap")
    axis.set_xticks(range(len(cols)))
    axis.set_yticks(range(len(cols)))
    axis.set_xticklabels(cols, rotation=45, ha="right")
    axis.set_yticklabels(cols)
    fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    path = save_figure(fig, report_dir / "correlation_heatmap.png")
    return visualization_payload("Correlation Heatmap", "correlation_heatmap", path)


def create_missing_value_matrix(dataframe: pd.DataFrame, report_dir: Path, target_column: str | None = None) -> dict | None:
    if dataframe.empty:
        return None

    cols = list(dataframe.columns[:40])
    matrix = dataframe[cols].isna().astype(int).head(250).T
    fig, axis = plt.subplots(figsize=(10, max(4, len(cols) * 0.24)))
    axis.imshow(matrix, aspect="auto", cmap="Greys")
    axis.set_title("Missing Value Matrix")
    axis.set_xlabel("Rows")
    axis.set_ylabel("Columns")
    axis.set_yticks(range(len(cols)))
    axis.set_yticklabels(cols)
    path = save_figure(fig, report_dir / "missing_value_matrix.png")
    return visualization_payload("Missing Value Matrix", "missing_value_matrix", path)


def create_class_distribution(dataframe: pd.DataFrame, report_dir: Path, target_column: str | None = None) -> dict | None:
    if not target_column or target_column not in dataframe.columns:
        return None

    counts = dataframe[target_column].fillna("<missing>").astype(str).value_counts()
    if counts.empty:
        return None

    fig, axis = plt.subplots(figsize=(8, 4.5))
    counts.plot(kind="bar", ax=axis, color="#2563eb")
    axis.set_title(f"Class Distribution: {target_column}")
    axis.set_xlabel(target_column)
    axis.set_ylabel("Count")
    path = save_figure(fig, report_dir / "class_distribution.png")
    return visualization_payload("Class Distribution", "class_distribution", path)


def create_scatter_plot(dataframe: pd.DataFrame, report_dir: Path, target_column: str | None = None) -> dict | None:
    cols = [column for column in numeric_columns(dataframe) if column != target_column]
    if len(cols) < 2:
        return None

    x_column, y_column = cols[:2]
    sample = dataframe[[x_column, y_column]].dropna()
    if sample.empty:
        return None

    sample = sample.sample(min(len(sample), 1000), random_state=42)
    fig, axis = plt.subplots(figsize=(8, 5))
    axis.scatter(sample[x_column], sample[y_column], alpha=0.65, color="#0f766e")
    axis.set_title(f"Scatter Plot: {x_column} vs {y_column}")
    axis.set_xlabel(str(x_column))
    axis.set_ylabel(str(y_column))
    path = save_figure(fig, report_dir / "scatter_plot.png")
    return visualization_payload("Scatter Plot", "scatter_plot", path)


def save_figure(fig, path: Path) -> Path:
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return path


def visualization_payload(title: str, kind: str, path: Path) -> dict:
    relative_path = path.relative_to(REPORTS_ROOT.parent).as_posix()
    return {
        "title": title,
        "type": kind,
        "path": str(path),
        "url": f"/reports/{relative_path}",
    }


def infer_target_column(dataframe: pd.DataFrame, requested_target: str | None) -> str | None:
    if requested_target and requested_target in dataframe.columns:
        return requested_target

    preferred_names = ("target", "label", "class", "survived", "outcome")
    lower_lookup = {str(column).lower(): column for column in dataframe.columns}

    for name in preferred_names:
        column = lower_lookup.get(name)
        if column is not None and is_class_like(dataframe[column]):
            return str(column)

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


def numeric_columns(dataframe: pd.DataFrame) -> list[str]:
    return [str(column) for column in dataframe.select_dtypes(include=["number"]).columns]


def categorical_columns(dataframe: pd.DataFrame) -> list[str]:
    return [
        str(column)
        for column in dataframe.columns
        if not pd.api.types.is_numeric_dtype(dataframe[column]) or pd.api.types.is_bool_dtype(dataframe[column])
    ]


def percentage(part: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def clean_number(value) -> float | int | None:
    if value is None or pd.isna(value):
        return None

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        value = float(value)

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return round(value, 6)

    return value


def to_jsonable(value):
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(item) for item in value]

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        value = float(value)

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return round(value, 6)

    if isinstance(value, np.ndarray):
        return [to_jsonable(item) for item in value.tolist()]

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(value, (str, int, bool)) or value is None:
        return value

    return str(value)


def render_html_report(report_data: dict) -> str:
    overview = report_data["dataset_overview"]
    visuals = report_data.get("visualizations", [])

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>EDA Report - {escape(overview["dataset_name"])}</title>
    <style>
      body {{ margin: 0; padding: 32px; font-family: Arial, sans-serif; color: #18211f; background: #f6f7f4; }}
      main {{ max-width: 1100px; margin: 0 auto; background: #fff; border: 1px solid #d9ded8; border-radius: 8px; padding: 24px; }}
      h1, h2 {{ margin-top: 0; }}
      section {{ border-top: 1px solid #d9ded8; padding-top: 18px; margin-top: 18px; }}
      table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
      th, td {{ border-bottom: 1px solid #d9ded8; padding: 8px; text-align: left; vertical-align: top; }}
      th {{ background: #eef3f1; }}
      .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
      .metric {{ border-left: 3px solid #0f766e; padding-left: 10px; }}
      .metric span {{ display: block; color: #66736f; font-size: 12px; text-transform: uppercase; }}
      img {{ max-width: 100%; border: 1px solid #d9ded8; border-radius: 6px; margin: 10px 0 18px; }}
    </style>
  </head>
  <body>
    <main>
      <h1>EDA Report: {escape(overview["dataset_name"])}</h1>
      <p>Generated at {escape(report_data.get("generated_at", ""))}</p>
      <section>
        <h2>Dataset Overview</h2>
        {overview_metrics(overview)}
      </section>
      <section>
        <h2>Column Analysis</h2>
        {table_html(report_data["column_analysis"], ["name", "data_type", "unique_values", "missing_percentage", "example_values"])}
      </section>
      <section>
        <h2>Numerical Statistics</h2>
        {table_html(report_data["numerical_statistics"], ["column", "mean", "median", "mode", "minimum", "maximum", "standard_deviation", "variance", "quartiles"])}
      </section>
      <section>
        <h2>Categorical Analysis</h2>
        {table_html(report_data["categorical_analysis"], ["column", "most_common_category", "least_common_category", "cardinality", "missing_count", "frequency_counts"])}
      </section>
      <section>
        <h2>Missing Values</h2>
        {table_html(report_data["missing_value_analysis"], ["column", "missing_count", "missing_percentage"])}
      </section>
      <section>
        <h2>Highly Correlated Features</h2>
        {table_html(report_data["correlation_analysis"]["highly_correlated_features"], ["feature_1", "feature_2", "correlation"])}
      </section>
      <section>
        <h2>Outlier Detection</h2>
        {table_html(report_data["outlier_detection"], ["column", "outlier_count", "outlier_percentage", "lower_bound", "upper_bound"])}
      </section>
      <section>
        <h2>Visualizations</h2>
        {visuals_html(visuals)}
      </section>
    </main>
  </body>
</html>
"""


def overview_metrics(overview: dict) -> str:
    labels = [
        ("Rows", overview["rows"]),
        ("Columns", overview["columns"]),
        ("Missing Values", overview["total_missing_values"]),
        ("Duplicate Rows", overview["duplicate_rows"]),
        ("Memory Usage", format_bytes(overview["memory_usage_bytes"])),
        ("File Size", format_bytes(overview["file_size_bytes"])),
        ("Duplicate %", f'{overview["duplicate_percentage"]}%'),
    ]
    items = "".join(f"<div class='metric'><span>{escape(label)}</span><strong>{escape(value)}</strong></div>" for label, value in labels)
    return f"<div class='metrics'>{items}</div>"


def table_html(rows: list[dict], columns: list[str]) -> str:
    if not rows:
        return "<p>No data available.</p>"

    header = "".join(f"<th>{escape(column.replace('_', ' ').title())}</th>" for column in columns)
    body = ""
    for row in rows:
        body += "<tr>"
        for column in columns:
            body += f"<td>{escape(row.get(column))}</td>"
        body += "</tr>"

    return f"<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"


def visuals_html(visuals: list[dict]) -> str:
    if not visuals:
        return "<p>No visualizations generated.</p>"

    return "".join(
        f"<h3>{escape(visual['title'])}</h3><img src='{escape(visual['url'])}' alt='{escape(visual['title'])}' />"
        for visual in visuals
    )


def escape(value) -> str:
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    return html.escape(str(value))


def format_bytes(bytes_value: int) -> str:
    if not bytes_value:
        return "0 B"

    units = ("B", "KB", "MB", "GB")
    index = min(int(math.log(bytes_value, 1024)), len(units) - 1)
    value = bytes_value / (1024**index)
    return f"{value:.1f} {units[index]}" if index else f"{int(value)} {units[index]}"


def log_activity(db: Session, project_id: int, activity_type: str, message: str | None = None) -> Activity:
    activity = Activity(
        project_id=project_id,
        activity_type=activity_type,
        message=message,
    )
    db.add(activity)
    return activity
