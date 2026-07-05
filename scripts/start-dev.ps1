$ErrorActionPreference = "Stop"

Write-Host "Starting MLForge AI infrastructure..."
docker compose up -d

Write-Host "Starting FastAPI on http://127.0.0.1:8000"
Set-Location "$PSScriptRoot\..\backend"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
