# Troubleshooting

## MLflow Login

This local setup does not configure MLflow authentication.

Open:

```text
http://localhost:5000
```

If a login appears, check that you are not opening another service, browser extension, company proxy, or cached page.

## Check Containers

```powershell
docker ps --filter "name=mlforge"
```

Expected containers:

- `mlforge-postgres`
- `mlforge-pgadmin`
- `mlforge-qdrant`
- `mlforge-mlflow`

## Restart Infrastructure

```powershell
docker compose up -d
```

## FastAPI Command

Run from `backend/`:

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Database Connection

Default database URL:

```text
postgresql://postgres:postgres@localhost:5432/mlforge_ai
```

Create the `mlforge_ai` database in pgAdmin if FastAPI fails at startup.

## Qdrant Health

```powershell
curl.exe http://localhost:6333/collections
```

## MLflow Health

```powershell
curl.exe http://localhost:5000/health
```

Expected response:

```text
OK
```
