import html
import json


def render_training_report(summary: dict) -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Training Report - {escape(summary["target_column"])}</title>
    <style>
      body {{ margin: 0; padding: 32px; font-family: Arial, sans-serif; color: #18211f; background: #f6f7f4; }}
      main {{ max-width: 1100px; margin: 0 auto; background: #fff; border: 1px solid #d9ded8; border-radius: 8px; padding: 24px; }}
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
      <h1>Training Report</h1>
      <section>
        <h2>Summary</h2>
        {summary_metrics(summary)}
      </section>
      <section>
        <h2>Model Comparison</h2>
        {comparison_table(summary["model_results"])}
      </section>
      <section>
        <h2>Best Model Metrics</h2>
        {dict_table(summary["best_metrics"])}
      </section>
    </main>
  </body>
</html>
"""


def summary_metrics(summary: dict) -> str:
    labels = [
        ("Problem", summary["problem_type"]),
        ("Target", summary["target_column"]),
        ("Models", len(summary["selected_models"])),
        ("Best", summary["best_model"]),
        ("Training Time", f'{summary["training_time"]:.2f}s'),
        ("Optimized", ", ".join(summary.get("optimized_models", [])) or "None"),
    ]
    items = "".join(f"<div class='metric'><span>{escape(label)}</span><strong>{escape(value)}</strong></div>" for label, value in labels)
    return f"<div class='metrics'>{items}</div>"


def comparison_table(results: list[dict]) -> str:
    if not results:
        return "<p>No results.</p>"

    rows = ""
    for result in results:
        rows += "<tr>"
        rows += f"<td>{escape(result['model'])}</td>"
        rows += f"<td>{escape(result.get('score'))}</td>"
        rows += f"<td>{escape(result.get('training_time'))}</td>"
        rows += f"<td>{escape(result.get('inference_time'))}</td>"
        rows += f"<td>{escape(result.get('metrics'))}</td>"
        rows += "</tr>"

    return (
        "<table><thead><tr><th>Model</th><th>Score</th><th>Training Time</th>"
        "<th>Inference Time</th><th>Metrics</th></tr></thead><tbody>"
        f"{rows}</tbody></table>"
    )


def dict_table(value: dict) -> str:
    rows = "".join(f"<tr><th>{escape(key)}</th><td>{escape(item)}</td></tr>" for key, item in value.items())
    return f"<table><tbody>{rows}</tbody></table>"


def escape(value) -> str:
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    return html.escape(str(value))
