# 🚀 MLForge AI

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <br>
  <img src="https://img.shields.io/badge/CrewAI-FF5A5F?style=for-the-badge" alt="CrewAI">
  <img src="https://img.shields.io/badge/LlamaIndex-8A2BE2?style=for-the-badge" alt="LlamaIndex">
  <img src="https://img.shields.io/badge/Qdrant-1A1A1A?style=for-the-badge&logo=qdrant&logoColor=white" alt="Qdrant">
  <img src="https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white" alt="MLflow">
</div>

<p align="center">
  <strong>An Intelligent Machine Learning Platform powered by Multi-Agent AI and Advanced RAG</strong>
</p>

---

## 📖 Project Overview

**MLForge AI** is an advanced, end-to-end Machine Learning platform that automates the entire data science lifecycle. By integrating **CrewAI** for multi-agent workflows and **LlamaIndex/Qdrant** for Retrieval-Augmented Generation (RAG), MLForge AI empowers users to upload datasets, perform Exploratory Data Analysis (EDA), clean data, engineer features, train models, and generate comprehensive reports—all through an intuitive web interface.

Whether you're a data scientist looking to accelerate your workflow or a developer building AI-powered applications, MLForge AI provides the tools, infrastructure, and intelligence to streamline the ML journey.

## ✨ Key Features

- **End-to-End ML Pipeline Workflow**: Step-by-step guidance from dataset upload to model training and evaluation.
- **Multi-Agent AI Automation (CrewAI)**: Intelligent agents that analyze data, recommend cleaning strategies, and suggest features.
- **Knowledge Base & RAG (LlamaIndex + Qdrant)**: Store, index, and query documents seamlessly to augment the AI assistant's knowledge.
- **Experiment Tracking (MLflow)**: Automatically log parameters, metrics, and models for complete reproducibility.
- **Automated EDA**: Generate summary statistics, correlation matrices, and visualizations instantly.
- **Interactive Data Cleaning**: Handle missing values, outliers, and duplicates with smart AI recommendations.
- **Feature Engineering**: Scale, encode, and transform features with ease.
- **Model Training & Explainability**: Train algorithms like Random Forest and visualize model decisions using SHAP.
- **Modern Tech Stack**: Built with FastAPI, React, PostgreSQL, Docker, and cutting-edge AI libraries.

---

## 🎥 Demo Video

Watch the complete demonstration of MLForge AI in action:

[**👉 Watch the MLForge AI Demo Video on Google Drive**](https://drive.google.com/file/d/1EGdwztjm6BUEkQegZsd01wMQT1ffi7mP/view?usp=sharing)

---

## 📸 Screenshots & Workflow Highlights

Here is a visual walkthrough of the MLForge AI platform. All screenshots are available in the `docs/Screenshots` folder.

### Dashboard & Setup
| Home Dashboard | Project Creation |
|:---:|:---:|
| <img src="docs/Screenshots/01-home-dashboard.png" width="400"> | <img src="docs/Screenshots/02-pipeline-step1-project.png" width="400"> |

### Data Pipeline
| Dataset Upload | Exploratory Data Analysis (EDA) |
|:---:|:---:|
| <img src="docs/Screenshots/03-pipeline-step2-upload.png" width="400"> | <img src="docs/Screenshots/04-pipeline-step3-eda.png" width="400"> |

| EDA Visualizations | Data Cleaning |
|:---:|:---:|
| <img src="docs/Screenshots/05-eda-visualizations.png" width="400"> | <img src="docs/Screenshots/06-pipeline-step4-cleaning.png" width="400"> |

| Feature Engineering | Model Training |
|:---:|:---:|
| <img src="docs/Screenshots/07-pipeline-step5-features.png" width="400"> | <img src="docs/Screenshots/08-pipeline-step6-training.png" width="400"> |

### Reporting & Tracking
| Final Report Generation | MLflow Experiments Tracking |
|:---:|:---:|
| <img src="docs/Screenshots/09-pipeline-step7-report.png" width="400"> | <img src="docs/Screenshots/10-experiments-tracking.png" width="400"> |

### AI Assistant & Infrastructure
| AI Assistant Interface | Knowledge Base & RAG |
|:---:|:---:|
| <img src="docs/Screenshots/11-ai-assistant.png" width="400"> | <img src="docs/Screenshots/12-knowledge-base-rag.png" width="400"> |

| MLflow Dashboard | Qdrant Collections |
|:---:|:---:|
| <img src="docs/Screenshots/13-mlflow-experiments.png" width="400"> | <img src="docs/Screenshots/14-qdrant-collections.png" width="400"> |

| Qdrant Vectors | Dev Environment |
|:---:|:---:|
| <img src="docs/Screenshots/15-qdrant-vectors.png" width="400"> | <img src="docs/Screenshots/16-dev-environment.png" width="400"> |

| Postgres Tables | Postgres Database |
|:---:|:---:|
| <img src="docs/Screenshots/17-postgres-tables.png" width="400"> | <img src="docs/Screenshots/18-postgres-database.png" width="400"> |

---

## 🏗️ Architecture Explanation

MLForge AI is built using a modern, decoupled microservices architecture designed for scalability and performance.

1. **Frontend (React)**: A responsive, component-based user interface built with React and styled elegantly to provide a seamless user experience. It communicates with the backend via RESTful APIs.
2. **Backend (FastAPI)**: The core engine of the platform. It handles API requests, orchestrates the ML pipeline, interacts with the database, and manages AI agents. FastAPI ensures high performance and automatic interactive API documentation.
3. **Database (PostgreSQL)**: Stores application metadata, project details, dataset configurations, and pipeline states.
4. **Vector Database (Qdrant)**: Stores high-dimensional embeddings generated from documents, enabling fast and semantic search for the Retrieval-Augmented Generation (RAG) system.
5. **Experiment Tracking (MLflow)**: Logs all model training runs, hyperparameters, and evaluation metrics, acting as a central registry for machine learning experiments.
6. **AI Orchestration (CrewAI)**: Manages specialized autonomous agents (e.g., Data Analyst Agent, Feature Engineer Agent) that collaborate to perform complex data science tasks.
7. **RAG Framework (LlamaIndex)**: Connects custom data (PDFs, texts) to Large Language Models (LLMs), allowing the AI assistant to answer questions based on a specific knowledge base.

---

## 🚀 End-to-End Workflow

1. **Create Project**: Initialize a new ML workspace.
2. **Upload Dataset**: Ingest CSV/Excel files into the system.
3. **Exploratory Data Analysis**: AI automatically profiles the data and generates insights.
4. **Data Cleaning**: The Data Cleaning Agent recommends and applies imputation and outlier handling.
5. **Feature Engineering**: Transform variables based on AI suggestions.
6. **Model Training**: Train supervised learning models with automated MLflow tracking.
7. **Reporting & Explainability**: Generate a comprehensive performance report and SHAP explanations.
8. **AI Assistant Query**: Ask questions about the data or ML concepts using the RAG-powered chatbot.

---

## 💻 Tech Stack

- **Frontend**: React, React Router, Tailwind CSS (or Custom CSS), Axios, Recharts (for visualizations).
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Uvicorn, Pandas, Scikit-learn, SHAP.
- **AI / LLM**: OpenAI GPT models (or open-source alternatives), CrewAI, LlamaIndex.
- **Databases**: PostgreSQL (Relational), Qdrant (Vector).
- **MLOps**: MLflow (Experiment Tracking).
- **Infrastructure**: Docker, Docker Compose.

---

## 📂 Folder Structure

```text
ML-Forge-AI/
├── backend/                  # FastAPI backend application
│   ├── app/                  # Application code
│   │   ├── api/              # API routing and endpoints
│   │   ├── core/             # Core configurations (DB, security)
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── schemas/          # Pydantic schemas for validation
│   │   ├── services/         # Business logic (ML pipeline, AI agents)
│   │   └── utils/            # Helper functions
│   ├── requirements.txt      # Backend dependencies
│   └── main.py               # Application entry point
├── frontend/                 # React frontend application
│   ├── public/               # Static assets
│   ├── src/                  # React source code
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Page layouts
│   │   ├── services/         # API integration
│   │   └── App.js            # Main React component
│   └── package.json          # Frontend dependencies
├── docker/                   # Dockerfiles and configuration
├── docs/                     # Documentation and Screenshots
├── notebooks/                # Jupyter notebooks for prototyping
├── datasets/                 # Sample datasets directory
├── experiments/              # Local MLflow runs directory
├── .env.example              # Example environment variables
├── docker-compose.yml        # Multi-container orchestration
└── README.md                 # Project documentation
```

---

## ⚙️ Installation Guide

### Prerequisites

Ensure you have the following installed:
- Git
- Docker & Docker Compose
- Node.js (v16+) - *for local frontend development*
- Python (3.10+) - *for local backend development*
- An OpenAI API Key (or supported LLM provider key)

### Local Setup (Without Docker)

**1. Clone the repository**
```bash
git clone https://github.com/rai-wasif/ML-Forge-AI.git
cd ML-Forge-AI
```

**2. Setup Backend**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Edit .env and add your API keys/DB credentials
uvicorn app.main:app --reload --port 8000
```

**3. Setup Frontend**
```bash
cd ../frontend
npm install
npm start
```

---

## 🐳 Docker Setup (Recommended)

The easiest way to run MLForge AI is using Docker Compose, which spins up the Backend, Frontend, PostgreSQL DB, Qdrant, and MLflow simultaneously.

**1. Clone the repository**
```bash
git clone https://github.com/rai-wasif/ML-Forge-AI.git
cd ML-Forge-AI
```

**2. Configure Environment Variables**
Copy the example environment file and add your actual API keys.
```bash
cp .env.example .env
```
*Ensure you set `OPENAI_API_KEY` in the `.env` file.*

**3. Build and Run the Containers**
```bash
docker-compose up --build -d
```

**4. Access the Services**
- **Frontend App**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend / Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MLflow UI**: [http://localhost:5000](http://localhost:5000)
- **Qdrant Dashboard**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

## 🔑 Environment Variables

Here are the key environment variables used in the `.env` file:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# PostgreSQL Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/mlforge

# Qdrant Vector Database
QDRANT_URL=http://qdrant:6333

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000

# App Settings
ENVIRONMENT=development
SECRET_KEY=your_super_secret_key
```

---

## 🌐 Core API Endpoints

The FastAPI backend provides a comprehensive REST API. Some of the core endpoints include:

- `POST /api/projects/` - Create a new ML project.
- `POST /api/datasets/upload/` - Upload a dataset for a project.
- `GET /api/pipeline/{project_id}/eda/` - Run Exploratory Data Analysis.
- `POST /api/pipeline/{project_id}/train/` - Initiate model training.
- `POST /api/ai/chat/` - Chat with the AI Assistant.
- `POST /api/knowledge/upload/` - Upload a document to the RAG Knowledge Base.

*Visit `/docs` on the running backend for the interactive Swagger API reference.*

---

## 🧠 ML Pipeline Explanation

The automated ML pipeline follows a sequential, state-driven workflow:
1. **Ingestion**: Raw data is loaded into Pandas DataFrames and stored securely.
2. **Profiling**: Generates metadata (types, missing values, cardinality).
3. **Preprocessing**: Automatically applies one-hot encoding, standard scaling, and mean/median imputation based on data types and CrewAI recommendations.
4. **Training**: Uses `scikit-learn` to train baseline models (e.g., Random Forest Classifier/Regressor).
5. **Evaluation**: Calculates metrics like Accuracy, F1-Score, RMSE, and R2.
6. **Logging**: All parameters, metrics, and serialized models (`.pkl`) are logged to MLflow.

---

## 🤖 CrewAI Agent Descriptions

MLForge AI utilizes specialized agents to simulate a real data science team:

- **Senior Data Analyst Agent**: Responsible for inspecting data, identifying patterns, and suggesting EDA strategies.
- **Data Quality Engineer Agent**: Focuses on identifying data anomalies, missing values, and outliers, providing robust cleaning scripts.
- **Feature Engineering Specialist Agent**: Analyzes relationships and suggests new composite features to improve model predictive power.
- **Machine Learning Engineer Agent**: Recommends the best algorithms, hyperparameter tuning strategies, and evaluation metrics for the specific dataset.

---

## 📚 LlamaIndex + Qdrant RAG Explanation

The AI Assistant is supercharged with a **Retrieval-Augmented Generation (RAG)** pipeline:
1. **Document Upload**: Users upload domain-specific documents (PDF, TXT).
2. **Parsing & Chunking**: LlamaIndex parses the text and splits it into manageable chunks.
3. **Embedding**: Chunks are converted into vector embeddings using OpenAI's embedding models.
4. **Vector Storage**: Embeddings are stored efficiently in **Qdrant**.
5. **Retrieval & Generation**: When a user asks a question, the system queries Qdrant for the most relevant context and feeds it to the LLM to generate an accurate, context-aware response.

---

## 📊 MLflow Experiment Tracking

MLflow is integrated natively to ensure reproducibility. Every time a model is trained:
- **Parameters** (e.g., `n_estimators`, `max_depth`) are logged.
- **Metrics** (e.g., `accuracy`, `rmse`) are recorded.
- **Artifacts** (the trained model and SHAP summary plots) are saved.
You can compare different runs side-by-side using the MLflow UI.

---

## 🔍 SHAP Explainability

To ensure transparency, MLForge AI integrates **SHAP (SHapley Additive exPlanations)**.
After model training, the system generates SHAP summary plots that visualize which features had the highest impact on the model's predictions, ensuring that the AI's decisions are interpretable by human users.

---

## 🎯 Example Workflow

**Scenario: Predicting Customer Churn**
1. Create Project: "Telecom Churn Prediction"
2. Upload `telecom_data.csv`.
3. Go to **EDA**: See that `TotalCharges` has missing values and `ContractType` is highly correlated with churn.
4. Go to **Cleaning**: AI recommends median imputation for `TotalCharges`. Apply it.
5. Go to **Training**: Select `Random Forest`. The model trains and achieves 85% accuracy.
6. Go to **Report**: View the SHAP plot showing that `Month-to-month` contracts drive churn.
7. **AI Assistant**: Ask, *"Based on the uploaded Telecom guide in the Knowledge Base, what strategies reduce churn?"* -> Get a precise answer.

---

## 🔮 Future Improvements

- Add support for Deep Learning models (PyTorch/TensorFlow).
- Implement Auto-Hyperparameter Tuning (Optuna integration).
- Expand supported file types for dataset ingestion (Parquet, JSON).
- Add robust user authentication and role-based access control (RBAC).
- Implement model deployment (Model-as-a-Service) via one-click API generation.
- Add real-time streaming data support (Kafka integration).

---

## 🤝 Contribution Guide

We welcome contributions! To contribute:
1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

Please ensure you write tests for new features and adhere to the project's coding standards.

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Wasif Bhatti**
- **GitHub**: [Muhammad Wasif](https://github.com/rai-wasif)
- **LinkedIn**: [Muhammad Wasif](https://www.linkedin.com/in/rai-wasif)

*If you find this project useful, please consider giving it a ⭐ on GitHub!*
