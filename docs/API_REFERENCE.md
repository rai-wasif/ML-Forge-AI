# API Reference

Swagger is available at:

```text
http://127.0.0.1:8000/docs
```

## Projects

- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `PUT /projects/{project_id}`
- `DELETE /projects/{project_id}`

## Datasets

- `POST /datasets/upload`
- `GET /datasets/project/{project_id}`

## EDA

- `POST /eda/datasets/{dataset_id}/analyze`
- `GET /eda/datasets/{dataset_id}/latest`
- `GET /eda/reports/{report_id}/download`

## Cleaning

- `POST /cleaning/datasets/{dataset_id}/run`
- `GET /cleaning/datasets/{dataset_id}/latest`
- `GET /cleaning/reports/{report_id}/download`
- `GET /cleaning/reports/{report_id}/cleaned-dataset/download`

## Feature Engineering

- `POST /features/datasets/{dataset_id}/generate`
- `GET /features/datasets/{dataset_id}/latest`
- `GET /features/datasets/{dataset_id}/download`
- `GET /features/reports/{report_id}/download`

## Training, MLflow, SHAP, Reports

- `POST /training/datasets/{dataset_id}/train`
- `GET /training/datasets/{dataset_id}/latest`
- `GET /training/projects/{project_id}/experiments`
- `GET /training/projects/{project_id}/experiments/compare`
- `POST /training/reports/{report_id}/final-report`
- `GET /training/reports/{report_id}/download`
- `GET /training/reports/{report_id}/final-report/download`
- `GET /training/models/{report_id}/download`

## RAG

- `POST /rag/index`
- `POST /rag/query`
- `GET /rag/collections`
- `DELETE /rag/collections/{collection_name}`

## Agent Assistant

- `POST /agents/chat`

Example prompt:

```text
Analyze this Titanic dataset, train the best model, explain the result, and compare it with the previous experiment.
```
