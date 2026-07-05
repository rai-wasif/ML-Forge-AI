# MLForge AI

MLForge AI is an end-to-end AI/ML engineering workbench for tabular machine learning projects. It combines dataset management, EDA, cleaning, feature engineering, AutoML-style training, CrewAI orchestration, Qdrant RAG, MLflow tracking, SHAP explainability, and final AI reports in one FastAPI application.

## What It Does

- Create ML projects and upload CSV, Excel, or Parquet datasets.
- Generate EDA reports with statistics and visualizations.
- Clean datasets with missing value handling, duplicate removal, invalid value checks, and outlier handling.
- Generate model-ready features with encoding, scaling, and feature creation.
- Train and compare multiple ML models.
- Track experiments in MLflow.
- Generate SHAP feature importance reports.
- Index ML knowledge and generated reports into Qdrant.
- Ask the AI assistant to run pipelines, explain results, and compare experiments.
- Export HTML reports and model artifacts.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, PostgreSQL
- ML: pandas, scikit-learn, XGBoost, LightGBM, CatBoost, Optuna
- Agents: CrewAI-style orchestration layer
- RAG: LlamaIndex document loading, Qdrant vector search
- MLOps: MLflow
- Explainability: SHAP
- Frontend: Static HTML, CSS, JavaScript
- Infrastructure: Docker Compose

## Local Ports

| Service | URL |
| --- | --- |
| FastAPI | `http://127.0.0.1:8000` |
| Swagger | `http://127.0.0.1:8000/docs` |
| App UI | `http://127.0.0.1:8000/ui` |
| pgAdmin | `http://localhost:5050` |
| Qdrant | `http://localhost:6333` |
| MLflow | `http://localhost:5000` |

MLflow local UI does not need a login in this setup.

## Quick Start

1. Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --prefer-binary
```

3. Create `.env` from `.env.example` and add your keys.

4. Start infrastructure:

```powershell
docker compose up -d
```

5. Create the PostgreSQL database in pgAdmin:

```text
mlforge_ai
```

6. Run FastAPI:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

7. Open the app:

```text
http://127.0.0.1:8000/ui
```

## Demo Workflow

1. Open the UI.
2. Create a project, for example `Titanic Survival Prediction`.
3. Upload `datasets/sample/titanic/train.csv`.
4. Click `Analyze Dataset`.
5. Click `Clean Dataset`.
6. Click `Generate Features`.
7. Click `Train Model`.
8. Open MLflow at `http://localhost:5000`.
9. Review SHAP charts in the training report section.
10. Click `Generate AI Report`.
11. Ask the assistant: `Compare this experiment with the previous run.`

## Screenshots And Demo Video

Use [docs/SCREENSHOT_AND_VIDEO_GUIDE.md](docs/SCREENSHOT_AND_VIDEO_GUIDE.md) when you are ready to capture screenshots and record the demo video.

Recommended screenshots:

- Project dashboard
- Dataset upload
- EDA charts
- Training metrics
- SHAP explainability
- Experiment tracking
- MLflow UI
- Knowledge Base and Qdrant UI
- AI Assistant response

## GitHub Publishing

Use [docs/GITHUB_PUBLISHING.md](docs/GITHUB_PUBLISHING.md) after your screenshots and demo video are ready.

## Project Status

All 10 planned milestones are implemented:

1. Backend foundation
2. Project and dataset management
3. EDA engine
4. Cleaning and preprocessing
5. Feature engineering
6. AutoML training pipeline
7. Agent orchestration
8. Qdrant RAG knowledge layer
9. MLflow, SHAP, and AI reports
10. Final documentation and packaging

## Repository Layout

```text
backend/app/
  api/routes/          FastAPI endpoints
  agents/              Agent role modules
  database/            SQLAlchemy setup
  ml/                  EDA, cleaning, feature, training, tracking, explainability
  models/              Database models
  rag/                 Knowledge base, loaders, embeddings, Qdrant retrieval
  schemas/             Pydantic response/request schemas
  services/            Application orchestration services
frontend/public/       Static UI
datasets/sample/       Sample Titanic files
docs/                  Architecture, API, demo, troubleshooting
scripts/               Helper PowerShell scripts
```

## Notes

- Generated models, reports, uploads, and MLflow artifacts are stored under `backend/app/storage/` and ignored by Git.
- Secrets belong in `.env`, never in Git.
- The default RAG embedding backend is local hashing, so the knowledge base works without downloading a HuggingFace model.
