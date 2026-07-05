# Screenshot and Demo Video Guide

Use this file when you are ready to capture portfolio screenshots and record the demo video.

## Start The Project

Open PowerShell in the project root:

```powershell
cd "D:\MLFORGE AI"
docker compose up -d
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Open These Pages

| Page | URL |
| --- | --- |
| Project UI | `http://127.0.0.1:8000/ui` |
| Swagger API | `http://127.0.0.1:8000/docs` |
| MLflow UI | `http://localhost:5000` |
| Qdrant Dashboard | `http://localhost:6333/dashboard` |
| pgAdmin | `http://localhost:5050` |

## Screenshots To Capture

1. Dashboard after opening a project.
2. Dataset upload and metadata cards.
3. ML workflow pipeline progress.
4. EDA report visualizations.
5. Cleaning and feature engineering summaries.
6. Training report with metrics.
7. SHAP feature importance charts.
8. Experiment Tracking section.
9. MLflow UI showing the logged run.
10. Knowledge Base answer with sources.
11. AI Assistant response and plan.
12. Qdrant dashboard showing collections.
13. Swagger API docs.

## Demo Video Flow

Recommended video length: 5 to 10 minutes.

1. Show the project folder and briefly explain the stack.
2. Run `docker compose up -d`.
3. Start FastAPI with Uvicorn.
4. Open the Project UI.
5. Create or open `Titanic Survival Prediction`.
6. Upload `datasets/sample/titanic/train.csv`.
7. Run EDA.
8. Run cleaning.
9. Generate features.
10. Train models.
11. Show MLflow at `http://localhost:5000`.
12. Return to the app and show SHAP charts.
13. Generate the AI report.
14. Ask the assistant: `Compare this experiment with the previous run.`
15. Ask the Knowledge Base: `Why can logistic regression perform well on Titanic?`
16. Open Qdrant dashboard and show the knowledge collection.
17. End by showing the README and architecture docs.

## Short Portfolio Pitch

MLForge AI is an end-to-end AI/ML engineering platform that combines automated ML pipelines, agent orchestration, RAG, vector search, experiment tracking, explainability, and final report generation in a Dockerized FastAPI application.
