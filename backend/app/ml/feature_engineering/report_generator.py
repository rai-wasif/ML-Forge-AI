import html
import json


def render_feature_report(summary: dict, dataset_name: str) -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Feature Report - {escape(dataset_name)}</title>
    <style>
      body {{ margin: 0; padding: 32px; font-family: Arial, sans-serif; color: #18211f; background: #f6f7f4; }}
      main {{ max-width: 1000px; margin: 0 auto; background: #fff; border: 1px solid #d9ded8; border-radius: 8px; padding: 24px; }}
      section {{ border-top: 1px solid #d9ded8; padding-top: 18px; margin-top: 18px; }}
      h1, h2 {{ margin-top: 0; }}
      table {{ width: 100%; border-collapse: collapse; }}
      th, td {{ border-bottom: 1px solid #d9ded8; padding: 8px; text-align: left; }}
      th {{ background: #eef3f1; }}
      .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
      .metric {{ border-left: 3px solid #0f766e; padding-left: 10px; }}
      .metric span {{ display: block; color: #66736f; font-size: 12px; text-transform: uppercase; }}
    </style>
  </head>
  <body>
    <main>
      <h1>Feature Report: {escape(dataset_name)}</h1>
      <p>Generated at {escape(summary.get("created_at", ""))}</p>
      <section>
        <h2>Summary</h2>
        {summary_metrics(summary)}
      </section>
      <section>
        <h2>Feature Types</h2>
        {dict_table(summary["feature_types"])}
      </section>
      <section>
        <h2>Created Features</h2>
        {list_table(summary["features_created"])}
      </section>
      <section>
        <h2>Dropped Columns</h2>
        {list_table(summary["dropped_columns"])}
      </section>
      <section>
        <h2>Encoding</h2>
        {dict_table(summary["encoding_report"])}
      </section>
      <section>
        <h2>Scaling</h2>
        {dict_table(summary["scaling_report"])}
      </section>
    </main>
  </body>
</html>
"""


def summary_metrics(summary: dict) -> str:
    labels = [
        ("Original Columns", summary["original_columns"]),
        ("Final Columns", summary["final_columns"]),
        ("Encoding", summary["encoding_method"]),
        ("Scaling", summary["scaling_method"]),
        ("Target", summary.get("target_column") or "Not detected"),
        ("Features Created", len(summary["features_created"])),
        ("Dropped Columns", len(summary["dropped_columns"])),
    ]
    items = "".join(f"<div class='metric'><span>{escape(label)}</span><strong>{escape(value)}</strong></div>" for label, value in labels)
    return f"<div class='metrics'>{items}</div>"


def list_table(items: list[str]) -> str:
    if not items:
        return "<p>No records.</p>"
    rows = "".join(f"<tr><td>{escape(item)}</td></tr>" for item in items)
    return f"<table><tbody>{rows}</tbody></table>"


def dict_table(value: dict) -> str:
    if not value:
        return "<p>No records.</p>"
    rows = "".join(f"<tr><th>{escape(key)}</th><td>{escape(item)}</td></tr>" for key, item in value.items())
    return f"<table><tbody>{rows}</tbody></table>"


def escape(value) -> str:
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    return html.escape(str(value))
