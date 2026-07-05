# GitHub Publishing Guide

Follow this after screenshots are captured and the demo video is ready.

## Final Local Checks

```powershell
git status
docker compose ps
cd backend
..\.venv\Scripts\python.exe -B -c "from app.main import app; print('app ok')"
cd ..
node --check frontend/public/app.js
```

## Create A GitHub Repository

1. Create an empty repository on GitHub.
2. Do not add a README from GitHub because this project already has one.
3. Copy the repository URL.

## Connect And Push

```powershell
git remote add origin https://github.com/YOUR_USERNAME/mlforge-ai.git
git branch -M main
git push -u origin main
```

If `origin` already exists:

```powershell
git remote set-url origin https://github.com/YOUR_USERNAME/mlforge-ai.git
git push -u origin main
```

## Create A Release

Suggested tag:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

Release title:

```text
MLForge AI v1.0
```

Release summary:

```text
End-to-end AI/ML engineering platform with FastAPI, PostgreSQL, Docker, EDA, cleaning, feature engineering, AutoML training, CrewAI-style orchestration, LlamaIndex/Qdrant RAG, MLflow tracking, SHAP explainability, and AI-generated reports.
```

## Do Not Push

These are already ignored and should stay local:

- `.env`
- `.venv/`
- `backend/app/storage/`
- `__pycache__/`
- `.pytest_cache/`
- generated reports, uploads, models, and MLflow artifacts
