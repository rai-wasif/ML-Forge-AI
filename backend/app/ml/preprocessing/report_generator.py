import html
import json
import math


def render_cleaning_report(summary: dict, dataset_name: str) -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Cleaning Report - {escape(dataset_name)}</title>
    <style>
      body {{ margin: 0; padding: 32px; font-family: Arial, sans-serif; color: #18211f; background: #f6f7f4; }}
      main {{ max-width: 1000px; margin: 0 auto; background: #fff; border: 1px solid #d9ded8; border-radius: 8px; padding: 24px; }}
      section {{ border-top: 1px solid #d9ded8; padding-top: 18px; margin-top: 18px; }}
      h1, h2 {{ margin-top: 0; }}
      table {{ width: 100%; border-collapse: collapse; }}
      th, td {{ border-bottom: 1px solid #d9ded8; padding: 8px; text-align: left; vertical-align: top; }}
      th {{ background: #eef3f1; }}
      .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
      .metric {{ border-left: 3px solid #0f766e; padding-left: 10px; }}
      .metric span {{ display: block; color: #66736f; font-size: 12px; text-transform: uppercase; }}
    </style>
  </head>
  <body>
    <main>
      <h1>Cleaning Report: {escape(dataset_name)}</h1>
      <p>Generated at {escape(summary.get("created_at", ""))}</p>
      <section>
        <h2>Cleaning Summary</h2>
        {summary_metrics(summary)}
      </section>
      <section>
        <h2>Missing Values</h2>
        {table_html(summary["missing_value_report"]["filled_columns"], ["column", "missing_before", "strategy", "fill_value"])}
      </section>
      <section>
        <h2>Outliers</h2>
        {table_html(summary["outlier_report"]["columns"], ["column", "outlier_count", "strategy", "lower_bound", "upper_bound"])}
      </section>
      <section>
        <h2>Invalid Values</h2>
        {table_html(summary["invalid_value_report"]["invalid_values"], ["column", "invalid_count", "rule", "strategy"])}
      </section>
      <section>
        <h2>Data Type Corrections</h2>
        {table_html(summary["datatype_changes"], ["column", "from", "to"])}
      </section>
    </main>
  </body>
</html>
"""


def summary_metrics(summary: dict) -> str:
    labels = [
        ("Rows Before", summary["original_rows"]),
        ("Rows After", summary["final_rows"]),
        ("Columns Before", summary["original_columns"]),
        ("Columns After", summary["final_columns"]),
        ("Missing Before", summary["missing_values_before"]),
        ("Missing After", summary["missing_values_after"]),
        ("Duplicates Removed", summary["duplicates_removed"]),
        ("Outliers Handled", summary["outliers_handled"]),
        ("Target", summary.get("target_column") or "Not detected"),
    ]

    items = "".join(f"<div class='metric'><span>{escape(label)}</span><strong>{escape(value)}</strong></div>" for label, value in labels)
    return f"<div class='metrics'>{items}</div>"


def table_html(rows: list[dict], columns: list[str]) -> str:
    if not rows:
        return "<p>No records.</p>"

    header = "".join(f"<th>{escape(column.replace('_', ' ').title())}</th>" for column in columns)
    body = ""

    for row in rows:
        body += "<tr>"
        for column in columns:
            body += f"<td>{escape(row.get(column))}</td>"
        body += "</tr>"

    return f"<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"


def escape(value) -> str:
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        value = ""
    return html.escape(str(value))
