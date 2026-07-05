# Demo Script

Use this sequence for GitHub, LinkedIn, or interview demos.

## Start

```powershell
docker compose up -d
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/ui
```

## Demo Steps

1. Create project: `Titanic Survival Prediction`.
2. Upload `datasets/sample/titanic/train.csv`.
3. Show dataset metadata: rows, columns, missing values, duplicates.
4. Click `Analyze Dataset`.
5. Show EDA plots and statistics.
6. Click `Clean Dataset`.
7. Show missing values and duplicates handled.
8. Click `Generate Features`.
9. Show encoded/scaled/created features.
10. Click `Train Model`.
11. Open MLflow: `http://localhost:5000`.
12. Show logged params, metrics, and artifacts.
13. Return to the app and show SHAP feature importance.
14. Click `Generate AI Report`.
15. Ask assistant: `Compare this experiment with the previous run.`
16. Ask knowledge base: `Why can logistic regression perform well on Titanic?`

## Portfolio Pitch

MLForge AI demonstrates a full AI engineering stack:

- ML pipelines
- Agent orchestration
- RAG knowledge retrieval
- MLflow experiment tracking
- SHAP explainability
- Automated AI reports
- Dockerized infrastructure
