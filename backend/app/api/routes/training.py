from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.training import ExperimentComparisonRead, ExperimentSummary, FinalReportRead, TrainingReportRead
from app.services import training_service


router = APIRouter(prefix="/training", tags=["training"])


@router.post("/datasets/{dataset_id}/train", response_model=TrainingReportRead)
def train_dataset(
    dataset_id: int,
    target_column: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return training_service.train_dataset(db, dataset_id, target_column)


@router.get("/datasets/{dataset_id}/latest", response_model=TrainingReportRead | None)
def get_latest_training_report(dataset_id: int, db: Session = Depends(get_db)):
    return training_service.get_latest_report(db, dataset_id)


@router.get("/projects/{project_id}/experiments", response_model=list[ExperimentSummary])
def list_project_experiments(project_id: int, db: Session = Depends(get_db)):
    return training_service.list_project_experiments(db, project_id)


@router.get("/projects/{project_id}/experiments/compare", response_model=ExperimentComparisonRead)
def compare_project_experiments(project_id: int, db: Session = Depends(get_db)):
    return training_service.compare_project_experiments(db, project_id)


@router.post("/reports/{report_id}/final-report", response_model=FinalReportRead)
def generate_final_report(report_id: int, db: Session = Depends(get_db)):
    return training_service.generate_final_report(db, report_id)


@router.get("/models/{report_id}/download")
def download_model(report_id: int, db: Session = Depends(get_db)):
    report = training_service.get_report_or_404(db, report_id)
    return FileResponse(
        report.model_path,
        media_type="application/octet-stream",
        filename=f"best_model_dataset_{report.dataset_id}.pkl",
    )


@router.get("/reports/{report_id}/download")
def download_training_report(report_id: int, db: Session = Depends(get_db)):
    report = training_service.get_report_or_404(db, report_id)
    return FileResponse(
        report.report_path,
        media_type="text/html",
        filename=f"training_report_dataset_{report.dataset_id}.html",
    )


@router.get("/reports/{report_id}/final-report/download")
def download_final_report(report_id: int, db: Session = Depends(get_db)):
    report = training_service.get_report_or_404(db, report_id)
    if not report.final_report_path:
        payload = training_service.generate_final_report(db, report_id)
        path = payload["html_path"]
    else:
        path = report.final_report_path.replace(".md", ".html")

    return FileResponse(
        path,
        media_type="text/html",
        filename=f"final_ai_report_dataset_{report.dataset_id}.html",
    )
