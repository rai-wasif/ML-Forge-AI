<div align="center">

# MLForge AI

### End-to-End AI/ML Engineering Workbench for Tabular Machine Learning

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)](https://mlflow.org/)
[![Qdrant](https://img.shields.io/badge/Qdrant-DC244C?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Agents-8A2BE2?style=for-the-badge)](https://www.crewai.com/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-RAG-000000?style=for-the-badge)](https://www.llamaindex.ai/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![SHAP](https://img.shields.io/badge/SHAP-Explainability-FF6B6B?style=for-the-badge)](https://shap.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Build, train, explain, and document machine learning projects in one guided platform.**

[Live Demo Video](https://drive.google.com/file/d/1EGdwztjm6BUEkQegZsd01wMQT1ffi7mP/view?usp=sharing) · [GitHub Repository](https://github.com/rai-wasif/ML-Forge-AI) · [API Docs](http://127.0.0.1:8000/docs) · [Architecture](docs/ARCHITECTURE.md)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Why MLForge AI](#why-mlforge-ai)
- [Key Features](#key-features)
- [Demo Video](#demo-video)
- [Screenshots](#screenshots)
- [Architecture](#architecture)
- [End-to-End Workflow](#end-to-end-workflow)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Docker Setup](#docker-setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Frontend Overview](#frontend-overview)
- [ML Pipeline](#ml-pipeline)
- [CrewAI Agent System](#crewai-agent-system)
- [LlamaIndex + Qdrant RAG](#llamaindex--qdrant-rag)
- [MLflow Experiment Tracking](#mlflow-experiment-tracking)
- [SHAP Explainability](#shap-explainability)
- [API Endpoints](#api-endpoints)
- [Example Workflow](#example-workflow)
- [Knowledge Base Usage](#knowledge-base-usage)
- [Sample Prompts](#sample-prompts)
- [Local Service Ports](#local-service-ports)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Overview

**MLForge AI** is a production-style AI/ML engineering workbench that takes tabular datasets from raw upload to trained models, explainability charts, experiment tracking, and AI-generated reports — all inside a single FastAPI application with a professional step-by-step wizard UI.

The platform combines:

- Automated **EDA**, **cleaning**, **feature engineering**, and **AutoML training**
- **CrewAI-style agent orchestration** for natural-language pipeline execution
- **LlamaIndex + Qdrant RAG** for ML knowledge retrieval
- **MLflow** experiment tracking and artifact logging
- **SHAP** model explainability
- **Dockerized infrastructure** (PostgreSQL, Qdrant, MLflow, pgAdmin)

Whether you are building a portfolio project, running a classroom demo, or prototyping an internal ML platform, MLForge AI gives you a complete, recruiter-friendly stack in one repository.

---

## Why MLForge AI

Most ML portfolio projects stop at a Jupyter notebook or a single-model API. MLForge AI goes further by demonstrating **full-stack AI engineering**:

| Capability | What It Proves |
|---|---|
| ML Pipelines | End-to-end tabular ML from upload to deployment-ready artifacts |
| MLOps | MLflow logging, experiment comparison, model downloads |
| Explainability | SHAP importance and summary plots |
| Agentic AI | Multi-step orchestration from natural language |
| RAG | Document indexing, vector search, grounded answers |
| Infrastructure | Docker Compose, PostgreSQL, vector DB, tracking server |
| Product UX | Guided 7-step wizard instead of a confusing single-page UI |

---

## Key Features

### Project & Dataset Management
- Create and manage ML projects with descriptions and metadata
- Upload **CSV**, **Excel**, or **Parquet** files
- Automatic dataset profiling: rows, columns, missing values, duplicates, memory usage
- Optional **target column** selection before pipeline execution

### Exploratory Data Analysis (EDA)
- Dataset overview statistics
- Numerical summaries, missing-value analysis, outlier detection
- Class balance for classification targets
- Auto-generated visualizations: histograms, box plots, correlation heatmaps, scatter plots, missing-value matrix

### Data Cleaning & Preprocessing
- Missing value imputation (median/mode strategies)
- Duplicate row removal
- Invalid value detection and correction
- IQR-based outlier clipping
- Downloadable cleaned dataset and HTML/JSON reports

### Feature Engineering
- Categorical encoding (one-hot + label)
- Numeric scaling (standard)
- Datetime feature extraction
- Useless column dropping and feature selection
- Export model-ready feature dataset as Parquet

### AutoML Training
- Automatic problem-type detection (classification / regression)
- Multi-model benchmarking: Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost
- Optuna hyperparameter tuning
- Best model selection with full metric comparison
- Downloadable trained model (`.pkl`) and training report

### Experiment Tracking (MLflow)
- Logs parameters, metrics, and artifacts per training run
- Project-scoped experiment history
- Side-by-side experiment comparison in the UI
- Direct link to MLflow dashboard

### SHAP Explainability
- Feature importance bar charts
- SHAP summary plots
- Top feature ranking table in the final report step

### AI Assistant (CrewAI Orchestration)
- Natural-language commands to run pipeline stages
- Planner, EDA, cleaning, feature, training, evaluation, research, and documentation agents
- Prompt chips for common tasks: analyze & train, compare runs, explain results
- Execution plan and structured response output

### Knowledge Base (RAG)
- Index PDF, Markdown, TXT, HTML, and JSON documents
- Auto-index built-in ML knowledge and generated pipeline reports
- Qdrant vector storage with cosine similarity search
- Grounded answers with source citations and relevance scores

### Professional Wizard UI
- **7-step guided pipeline**: Project → Upload → Explore → Clean → Features → Train → Report
- Clickable stepper with completion states
- Separate views for Home, Pipeline, Experiments, AI Assistant, and Knowledge Base
- Toast notifications, loading spinners, and live backend status indicator

---

## Demo Video

Watch the full walkthrough on Google Drive:

**[MLForge AI Demo Video](https://drive.google.com/file/d/1EGdwztjm6BUEkQegZsd01wMQT1ffi7mP/view?usp=sharing)**

The demo covers:
1. Starting Docker services and FastAPI
2. Creating a project and uploading a dataset
3. Running the full 7-step ML pipeline
4. Viewing MLflow experiments and SHAP charts
5. Using the AI Assistant and Knowledge Base
6. Exploring Qdrant vector collections and PostgreSQL tables

---

## Screenshots

### Home Dashboard — Create & Open Projects

![Home Dashboard](docs/Screenshots/01-home-dashboard.png)

Create a new ML project or open an existing one. The home screen is the starting point for every workflow.

---

### Step 1 — Project Setup

![Pipeline Step 1 — Project](docs/Screenshots/02-pipeline-step1-project.png)

The guided wizard shows project metadata and a clickable 7-step progress bar across the top.

---

### Step 2 — Dataset Upload

![Pipeline Step 2 — Upload](docs/Screenshots/03-pipeline-step2-upload.png)

Upload CSV, Excel, or Parquet files. View row/column stats and configure the target column before continuing.

---

### Step 3 — Exploratory Data Analysis

![Pipeline Step 3 — EDA](docs/Screenshots/04-pipeline-step3-eda.png)

Automated EDA with dataset overview, class balance tables, and downloadable HTML reports.

---

### EDA Visualizations

![EDA Visualizations](docs/Screenshots/05-eda-visualizations.png)

Correlation heatmap, missing-value matrix, class distribution, and scatter plots generated automatically.

---

### Step 4 — Data Cleaning

![Pipeline Step 4 — Cleaning](docs/Screenshots/06-pipeline-step4-cleaning.png)

Missing values filled, outliers handled, and a detailed cleaning report with before/after statistics.

---

### Step 5 — Feature Engineering

![Pipeline Step 5 — Features](docs/Screenshots/07-pipeline-step5-features.png)

Encoding, scaling, and feature preparation with original vs. final column counts and target detection.

---

### Step 6 — Model Training

![Pipeline Step 6 — Training](docs/Screenshots/08-pipeline-step6-training.png)

AutoML training compares multiple algorithms and surfaces the best model with accuracy, precision, recall, and ROC-AUC.

---

### Step 7 — Results & AI Report

![Pipeline Step 7 — Report](docs/Screenshots/09-pipeline-step7-report.png)

Pipeline complete view with best model summary, download links for reports/models, and AI-generated narrative report.

---

### Experiment Tracking

![Experiments Tracking](docs/Screenshots/10-experiments-tracking.png)

All MLflow-logged runs in one table with compare-experiments support and a direct MLflow UI link.

---

### AI Assistant

![AI Assistant](docs/Screenshots/11-ai-assistant.png)

Run the full ML pipeline from natural language. The CrewAI orchestration layer plans and executes each stage.

---

### Knowledge Base (RAG)

![Knowledge Base RAG](docs/Screenshots/12-knowledge-base-rag.png)

Upload documents, index them into Qdrant, and ask ML questions with grounded answers and source citations.

---

### MLflow Dashboard

![MLflow Experiments](docs/Screenshots/13-mlflow-experiments.png)

Logged metrics for every model: accuracy, precision, recall, F1, ROC-AUC, and per-model comparison scores.

---

### Qdrant Vector Database

![Qdrant Collections](docs/Screenshots/14-qdrant-collections.png)

The `mlforge_docs` collection stores embedded knowledge chunks for retrieval-augmented generation.

![Qdrant Vectors](docs/Screenshots/15-qdrant-vectors.png)

Each vector point carries payload metadata: source file, document type, chunk ID, and original text.

---

### Development Environment

![Dev Environment](docs/Screenshots/16-dev-environment.png)

VS Code workspace showing `docker-compose.yml`, sample datasets, and Uvicorn serving the FastAPI backend.

---

### PostgreSQL Database (pgAdmin)

![PostgreSQL Tables](docs/Screenshots/17-postgres-tables.png)

Seven application tables: `projects`, `datasets`, `eda_reports`, `cleaning_reports`, `feature_reports`, `training_reports`, and `activities`.

![PostgreSQL Database](docs/Screenshots/18-postgres-database.png)

The `mlforge_ai` database stores all project metadata, pipeline reports, and experiment references.

---

## Architecture

MLForge AI is organized into four layers:

```text
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER                          │
│   Wizard UI (HTML/CSS/JS)  ·  FastAPI REST  ·  Swagger    │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                 ORCHESTRATION LAYER                         │
│   Agent Service  ·  Planner  ·  Research (RAG)  ·  Analyst  │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    ML ENGINE LAYER                          │
│   EDA  ·  Cleaning  ·  Features  ·  Training  ·  SHAP      │
│   MLflow Tracker  ·  Report Generator  ·  Model Saver       │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                     DATA LAYER                              │
│   PostgreSQL  ·  Local Storage  ·  Qdrant  ·  MLflow        │
└─────────────────────────────────────────────────────────────┘
```

### Main Data Flow

```mermaid
flowchart LR
    A[User] --> B[Wizard UI / API]
    B --> C{Manual or Agent?}
    C -->|Manual| D[EDA]
    C -->|Agent| E[Agent Orchestrator]
    E --> D
    D --> F[Cleaning]
    F --> G[Feature Engineering]
    G --> H[AutoML Training]
    H --> I[MLflow Logging]
    H --> J[SHAP Explainability]
    I --> K[AI Report Generation]
    J --> K
    K --> L[Qdrant Indexing]
    L --> M[RAG Answers / Assistant]
```

For a deeper breakdown, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## End-to-End Workflow

The platform follows a structured 7-step pipeline:

| Step | Name | Action | Output |
|:---:|---|---|---|
| 1 | **Project** | Create or select a project | Project record in PostgreSQL |
| 2 | **Upload** | Upload CSV / Excel / Parquet | Dataset metadata + file storage |
| 3 | **Explore** | Run automated EDA | Statistics, plots, HTML report |
| 4 | **Clean** | Fix missing values, outliers, duplicates | Cleaned CSV + cleaning report |
| 5 | **Features** | Encode, scale, engineer columns | Feature Parquet + feature report |
| 6 | **Train** | Benchmark multiple ML models | Best model `.pkl`, metrics, MLflow run |
| 7 | **Report** | View results, SHAP, AI summary | Downloadable reports and artifacts |

Advanced features (Experiments, AI Assistant, Knowledge Base) live in separate sidebar views so they do not interrupt the core pipeline flow.

---

## Tech Stack

### Backend
| Technology | Role |
|---|---|
| **FastAPI** | REST API, file uploads, static UI serving |
| **SQLAlchemy** | ORM for PostgreSQL |
| **Pydantic** | Request/response validation |
| **Uvicorn** | ASGI server |

### Machine Learning
| Technology | Role |
|---|---|
| **pandas / NumPy** | Data manipulation |
| **scikit-learn** | Baseline models and preprocessing |
| **XGBoost / LightGBM / CatBoost** | Gradient boosting models |
| **Optuna** | Hyperparameter optimization |
| **SHAP** | Model explainability |
| **imbalanced-learn** | Class imbalance handling |

### AI / Agents / RAG
| Technology | Role |
|---|---|
| **CrewAI** | Multi-agent orchestration framework |
| **LlamaIndex** | Document loading, indexing, querying |
| **Qdrant** | Vector database for embeddings |
| **Groq** | LLM inference (optional, via API key) |
| **sentence-transformers** | Embedding models (optional) |

### MLOps & Infrastructure
| Technology | Role |
|---|---|
| **MLflow** | Experiment tracking and artifact store |
| **PostgreSQL 16** | Application database |
| **Docker Compose** | Container orchestration |
| **pgAdmin** | Database administration UI |

### Frontend
| Technology | Role |
|---|---|
| **HTML5 / CSS3 / JavaScript** | Step-by-step wizard UI (no framework) |
| **CSS Variables** | Dark-theme design system |

---

## Project Structure

```text
ML-Forge-AI/
├── backend/
│   └── app/
│       ├── main.py                 # FastAPI entry point
│       ├── api/routes/             # REST endpoints (8 modules)
│       ├── agents/                 # CrewAI agent roles
│       │   ├── planner/
│       │   ├── eda/
│       │   ├── cleaning/
│       │   ├── feature/
│       │   ├── training/
│       │   ├── evaluation/
│       │   ├── research/
│       │   └── documentation/
│       ├── services/               # Business logic orchestration
│       ├── ml/                     # EDA, cleaning, features, training, SHAP
│       ├── rag/                    # Knowledge base, embeddings, Qdrant
│       ├── models/                 # SQLAlchemy ORM models
│       ├── schemas/                # Pydantic schemas
│       ├── database/               # DB connection and init
│       ├── core/config.py          # Settings from .env
│       └── storage/                # Uploads, reports, models (gitignored)
├── frontend/
│   └── public/
│       ├── index.html              # App shell and sidebar
│       ├── app.js                  # Wizard logic and API client
│       └── styles.css              # Dark-theme design system
├── datasets/
│   └── sample/titanic/           # Demo CSV files
├── docs/
│   ├── Screenshots/                # UI and infrastructure screenshots
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── DEMO_SCRIPT.md
│   ├── TROUBLESHOOTING.md
│   └── GITHUB_PUBLISHING.md
├── scripts/
│   ├── start-dev.ps1
│   └── check-services.ps1
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── CHANGELOG.md
├── LICENSE
└── README.md
```

---

## Installation

### Prerequisites

- **Python 3.11+**
- **Docker Desktop** (for PostgreSQL, Qdrant, MLflow, pgAdmin)
- **Git**
- **8 GB+ RAM** recommended (ML training and optional embedding models)

### 1. Clone the Repository

```powershell
git clone https://github.com/rai-wasif/ML-Forge-AI.git
cd ML-Forge-AI
```

### 2. Create a Virtual Environment

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 3. Install Python Dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --prefer-binary
```

> **Note:** First install may take several minutes due to ML libraries (XGBoost, LightGBM, CatBoost, SHAP, LlamaIndex).

### 4. Configure Environment

```powershell
copy .env.example .env
```

Edit `.env` and add your API keys (optional for basic pipeline; required for LLM-powered features):

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mlforge_ai
GROQ_API_KEY=your_groq_key_here
GOOGLE_API_KEY=your_google_key_here
MLFLOW_TRACKING_URI=http://localhost:5000
MLFORGE_EMBEDDING_BACKEND=hashing
```

---

## Docker Setup

Start all infrastructure services:

```powershell
docker compose up -d
```

Verify containers are running:

```powershell
docker compose ps
```

Expected services:

| Container | Image | Purpose |
|---|---|---|
| `mlforge-postgres` | postgres:16 | Application database |
| `mlforge-pgadmin` | dpage/pgadmin4 | Database admin UI |
| `mlforge-qdrant` | qdrant/qdrant | Vector store for RAG |
| `mlforge-mlflow` | ghcr.io/mlflow/mlflow | Experiment tracking |

### Create the Database

1. Open pgAdmin at [http://localhost:5050](http://localhost:5050)
2. Login: `admin@example.com` / `admin123`
3. Connect to the PostgreSQL server (host: `postgres`, user: `postgres`, password: `postgres`)
4. Create a new database named: **`mlforge_ai`**

Tables are created automatically when FastAPI starts.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `GROQ_API_KEY` | No | — | Groq LLM API key for agent/RAG answers |
| `GOOGLE_API_KEY` | No | — | Google API key (alternative LLM) |
| `MLFLOW_TRACKING_URI` | No | `http://localhost:5000` | MLflow tracking server URL |
| `MLFORGE_EMBEDDING_BACKEND` | No | `hashing` | Embedding backend: `hashing` (local, no download) or `huggingface` |

> The default `hashing` embedding backend lets the Knowledge Base work offline without downloading HuggingFace models.

---

## Running the Application

### Option A — Manual Start

```powershell
# Terminal 1: Infrastructure (if not already running)
docker compose up -d

# Terminal 2: FastAPI backend
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### Option B — Dev Script

```powershell
.\scripts\start-dev.ps1
```

### Open the Application

| Page | URL |
|---|---|
| **App UI** | [http://127.0.0.1:8000/ui](http://127.0.0.1:8000/ui) |
| **Swagger API** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| **MLflow** | [http://localhost:5000](http://localhost:5000) |
| **Qdrant Dashboard** | [http://localhost:6333/dashboard](http://localhost:6333/dashboard) |
| **pgAdmin** | [http://localhost:5050](http://localhost:5050) |

---

## Frontend Overview

The UI is a **professional 7-step wizard** built with vanilla HTML, CSS, and JavaScript — no React build step required.

### Sidebar Navigation

| View | Purpose |
|---|---|
| **Home** | Create projects, open existing projects |
| **ML Pipeline** | Guided 7-step wizard |
| **Experiments** | MLflow run history and comparison |
| **AI Assistant** | Natural-language pipeline execution |
| **Knowledge Base** | Document indexing and RAG search |

### Wizard Steps

Each step shows:
- Step number badge ("Step 3 of 7")
- Clear title and description
- One primary action button
- Previous / Continue navigation
- Clickable stepper showing completion state

### UI Files

| File | Lines | Role |
|---|---|---|
| `frontend/public/index.html` | Shell layout, sidebar, toast container |
| `frontend/public/app.js` | State management, API calls, step rendering |
| `frontend/public/styles.css` | Dark-theme design system |

---

## ML Pipeline

### EDA Engine
- Computes numerical statistics, missing-value percentages, outlier counts
- Detects target column automatically (or uses user-selected column)
- Generates 6 visualization types saved as PNG artifacts
- Produces downloadable HTML and JSON reports

### Cleaning Engine
- Fills missing values using column-appropriate strategies
- Removes duplicate rows
- Detects and fixes invalid values
- Clips outliers using IQR bounds
- Exports cleaned CSV for downstream steps

### Feature Engineering Engine
- One-hot and label encoding for categoricals
- Standard scaling for numeric columns
- Datetime decomposition (year, month, day, etc.)
- Drops constant and near-constant columns
- Saves feature dataset as Parquet

### Training Engine
- Detects classification vs. regression automatically
- Trains and evaluates: Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost
- Runs Optuna tuning on top candidates
- Selects best model by ROC-AUC (classification) or R² (regression)
- Saves model pipeline, label encoder, and preprocessing artifacts
- Logs everything to MLflow

---

## CrewAI Agent System

MLForge AI includes a CrewAI-style multi-agent orchestration layer. Agents are mapped to pipeline stages:

| Agent | Role |
|---|---|
| **Planner Agent** | Parses user intent and builds an execution plan |
| **Dataset Agent** | Summarizes dataset metadata |
| **EDA Agent** | Runs or reuses exploratory analysis |
| **Cleaning Agent** | Executes data cleaning pipeline |
| **Feature Agent** | Generates model-ready features |
| **Training Agent** | Trains and evaluates models |
| **Evaluation Agent** | Summarizes model performance |
| **Research Agent** | Queries Qdrant knowledge base for ML context |
| **Documentation Agent** | Writes agent execution summary to storage |

### How It Works

1. User sends a natural-language prompt via `POST /agents/chat`
2. Agent service parses keywords (`analyze`, `clean`, `train`, `compare`, `explain`)
3. Required pipeline stages run in order (reusing existing reports when possible)
4. Research agent queries RAG for additional ML context
5. Structured response with execution plan and stage summaries is returned

Agent modules live in `backend/app/agents/`.

---

## LlamaIndex + Qdrant RAG

### Indexing Pipeline

1. **Document Loader** — reads PDF, MD, TXT, HTML, JSON from uploads or built-in knowledge
2. **Text Splitter** — chunks documents for embedding
3. **Embedder** — hashing (default) or HuggingFace sentence-transformers
4. **Qdrant Store** — stores vectors with metadata payload (source, title, chunk_id)
5. **Indexer** — orchestrates the full indexing flow

### Query Pipeline

1. User question is embedded
2. Qdrant retrieves top-K similar chunks (cosine similarity)
3. LlamaIndex query engine synthesizes a grounded answer
4. Response includes source citations and relevance scores

### Built-in ML Knowledge

Pre-loaded knowledge articles in `backend/app/rag/knowledge_base/machine_learning/`:
- Logistic Regression
- Feature Engineering
- Data Cleaning
- ROC-AUC Evaluation
- Overfitting

Generated pipeline reports are also auto-indexed when `include_reports=true`.

---

## MLflow Experiment Tracking

Every training run logs to MLflow:

- **Parameters**: target column, problem type, encoding/scaling methods, model names
- **Metrics**: accuracy, precision, recall, F1, ROC-AUC (classification) or R², RMSE (regression)
- **Per-model scores**: individual model comparison metrics
- **Artifacts**: model files, SHAP plots, training reports

Access the MLflow UI at [http://localhost:5000](http://localhost:5000) to browse runs, compare metrics, and inspect artifacts.

---

## SHAP Explainability

After training, the SHAP analyzer:

1. Loads the best model and feature dataset
2. Computes SHAP values for the test set
3. Generates feature importance bar chart
4. Generates SHAP summary plot
5. Returns top features with importance scores

SHAP artifacts appear in Step 7 (Report) and are included in the final AI report.

---

## API Endpoints

Full reference: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)  
Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Projects
```
POST   /projects
GET    /projects
GET    /projects/{id}
PUT    /projects/{id}
DELETE /projects/{id}
```

### Datasets
```
POST   /datasets/upload
GET    /datasets/project/{project_id}
```

### EDA
```
POST   /eda/datasets/{id}/analyze?target_column=optional
GET    /eda/datasets/{id}/latest
GET    /eda/reports/{id}/download
```

### Cleaning
```
POST   /cleaning/datasets/{id}/run?target_column=optional
GET    /cleaning/datasets/{id}/latest
GET    /cleaning/reports/{id}/download
GET    /cleaning/reports/{id}/cleaned-dataset/download
```

### Feature Engineering
```
POST   /features/datasets/{id}/generate?target_column=optional
GET    /features/datasets/{id}/latest
GET    /features/datasets/{id}/download
GET    /features/reports/{id}/download
```

### Training & Reports
```
POST   /training/datasets/{id}/train?target_column=optional
GET    /training/datasets/{id}/latest
GET    /training/projects/{id}/experiments
GET    /training/projects/{id}/experiments/compare
POST   /training/reports/{id}/final-report
GET    /training/reports/{id}/download
GET    /training/reports/{id}/final-report/download
GET    /training/models/{id}/download
```

### RAG / Knowledge Base
```
POST   /rag/index
POST   /rag/query
GET    /rag/collections
DELETE /rag/collections/{name}
```

### AI Assistant
```
POST   /agents/chat
```

---

## Example Workflow

### Titanic Survival Prediction (5-minute demo)

```text
1. Open http://127.0.0.1:8000/ui
2. Home → Create project: "Titanic Survival Prediction"
3. Pipeline Step 2 → Upload datasets/sample/titanic/train.csv
4. Set target column: "Survived" (or leave auto-detect)
5. Step 3 → Run Data Exploration → review charts
6. Step 4 → Clean Dataset → 0 missing values
7. Step 5 → Generate Features → 230 columns ready
8. Step 6 → Train Models → Logistic Regression wins
9. Step 7 → Download reports, view SHAP, generate AI report
10. Experiments → Compare runs in MLflow
11. AI Assistant → "Compare this experiment with the previous run"
12. Knowledge Base → "Why can logistic regression perform well on small datasets?"
```

Sample dataset files are included at `datasets/sample/titanic/`.

---

## Knowledge Base Usage

### Index Documents

1. Go to **Knowledge Base** in the sidebar
2. Upload PDF, Markdown, or text files
3. Set collection name (default: `mlforge_docs`)
4. Click **Index Documents**
5. Verify in Qdrant dashboard: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

### Ask Questions

1. Type a question in the search box
2. Click **Search Knowledge Base**
3. Review the grounded answer and source table

The indexer can also include:
- Built-in ML knowledge articles (`include_knowledge=true`)
- Generated pipeline reports (`include_reports=true`)

---

## Sample Prompts

### AI Assistant

```
Analyze my latest dataset and train the best model.
```

```
Compare this experiment with the previous run.
```

```
Why did Logistic Regression perform best on this dataset?
```

```
Run EDA, clean the data, and train an XGBoost model.
```

### Knowledge Base

```
Why can logistic regression beat XGBoost on a small dataset?
```

```
How does MLflow help in machine learning experiment tracking?
```

```
What is overfitting and how can I detect it?
```

```
Explain ROC-AUC and when to use it.
```

---

## Local Service Ports

| Service | Port | URL |
|---|---|---|
| FastAPI | 8000 | http://127.0.0.1:8000 |
| Swagger | 8000 | http://127.0.0.1:8000/docs |
| App UI | 8000 | http://127.0.0.1:8000/ui |
| PostgreSQL | 5432 | localhost:5432 |
| pgAdmin | 5050 | http://localhost:5050 |
| Qdrant REST | 6333 | http://localhost:6333 |
| Qdrant gRPC | 6334 | localhost:6334 |
| MLflow | 5000 | http://localhost:5000 |

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `Connection refused` on port 8000 | Start Uvicorn: `cd backend && uvicorn app.main:app --reload` |
| Database connection error | Ensure `mlforge_ai` database exists in pgAdmin |
| Docker containers not starting | Run `docker compose down` then `docker compose up -d` |
| MLflow not logging | Check `MLFLOW_TRACKING_URI=http://localhost:5000` in `.env` |
| Qdrant collection empty | Run **Index Documents** in Knowledge Base first |
| Training takes too long | Normal for Optuna tuning; House Prices dataset ~1-3 min |
| Agent returns generic answer | Add `GROQ_API_KEY` to `.env` for LLM-powered responses |

Full guide: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Future Improvements

- [ ] React/Next.js frontend with component library
- [ ] Real-time training progress via WebSockets
- [ ] User authentication and multi-tenant projects
- [ ] Cloud deployment (AWS/GCP/Azure) with Terraform
- [ ] Model deployment endpoint (REST inference API)
- [ ] Scheduled retraining and data drift detection
- [ ] Additional dataset connectors (S3, BigQuery, Snowflake)
- [ ] Jupyter notebook integration
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Kubernetes Helm chart for production deployment

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and add tests if applicable
4. Run linting: `black .`, `flake8`, `isort .`
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

Please do not commit `.env`, `.venv/`, or generated artifacts from `backend/app/storage/`.

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

```
Copyright (c) 2026 Wasif Bhatti
```

---

## Author

<div align="center">

**Wasif Bhatti**

AI/ML Engineer · Full-Stack Developer · MLOps Enthusiast

[![GitHub](https://img.shields.io/badge/GitHub-rai--wasif-181717?style=for-the-badge&logo=github)](https://github.com/rai-wasif)
[![Repository](https://img.shields.io/badge/Project-ML--Forge--AI-5B8CFF?style=for-the-badge)](https://github.com/rai-wasif/ML-Forge-AI)

Built with FastAPI · CrewAI · LlamaIndex · Qdrant · MLflow · SHAP

*If this project helped you, consider giving it a star on GitHub!*

</div>

---

<div align="center">

**MLForge AI v1.0** — From raw data to explained models in 7 steps.

[Watch Demo](https://drive.google.com/file/d/1EGdwztjm6BUEkQegZsd01wMQT1ffi7mP/view?usp=sharing) · [View on GitHub](https://github.com/rai-wasif/ML-Forge-AI) · [Report Bug](https://github.com/rai-wasif/ML-Forge-AI/issues)

</div>
