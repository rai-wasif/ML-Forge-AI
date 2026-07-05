# Architecture

MLForge AI is organized into four layers.

## 1. Interface Layer

- Static frontend served from `/ui`
- FastAPI REST endpoints
- Swagger docs at `/docs`

## 2. Orchestration Layer

- Agent service decides which pipeline steps to run.
- Research Agent uses Qdrant-backed RAG for ML knowledge and generated reports.
- Experiment Analyst compares previous training runs.

## 3. ML Engine Layer

- EDA engine creates statistics and plots.
- Cleaning engine handles missing values, duplicates, invalid values, and outliers.
- Feature engine creates model-ready datasets.
- Training engine evaluates multiple models and selects the best one.
- SHAP analyzer creates explainability artifacts.
- MLflow tracker logs experiment params, metrics, and artifacts.

## 4. Data Layer

- PostgreSQL stores projects, datasets, reports, activities, and experiment metadata.
- Local storage holds uploaded files, generated reports, models, and plots.
- Qdrant stores embedded knowledge chunks for retrieval.
- MLflow stores experiment metadata and artifacts.

## Main Flow

```text
User
  -> FastAPI/UI
  -> Agent or Manual Pipeline Action
  -> EDA / Cleaning / Features / Training
  -> MLflow + SHAP + Reports
  -> Qdrant Index
  -> Assistant Answers and Final Reports
```

## Service Ports

- FastAPI: `8000`
- PostgreSQL: `5432`
- pgAdmin: `5050`
- Qdrant REST: `6333`
- Qdrant gRPC: `6334`
- MLflow: `5000`
