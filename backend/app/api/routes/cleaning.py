from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.cleaning import CleaningReportRead
from app.services import cleaning_service


router = APIRouter(prefix="/cleaning", tags=["cleaning"])


@router.post("/datasets/{dataset_id}/run", response_model=CleaningReportRead)
def run_cleaning(
    dataset_id: int,
    target_column: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return cleaning_service.run_cleaning(db, dataset_id, target_column)


@router.get("/datasets/{dataset_id}/latest", response_model=CleaningReportRead | None)
def get_latest_cleaning_report(dataset_id: int, db: Session = Depends(get_db)):
    return cleaning_service.get_latest_report(db, dataset_id)


@router.get("/reports/{report_id}/download")
def download_cleaning_report(report_id: int, db: Session = Depends(get_db)):
    report = cleaning_service.get_report_or_404(db, report_id)
    return FileResponse(
        report.report_path,
        media_type="text/html",
        filename=f"cleaning_report_dataset_{report.dataset_id}.html",
    )


@router.get("/reports/{report_id}/cleaned-dataset/download")
def download_cleaned_dataset(report_id: int, db: Session = Depends(get_db)):
    report = cleaning_service.get_report_or_404(db, report_id)
    return FileResponse(
        report.cleaned_dataset_path,
        media_type="text/csv",
        filename=f"cleaned_dataset_{report.dataset_id}.csv",
    )
