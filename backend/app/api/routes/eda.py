from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.eda import EDAReportRead
from app.services import eda_service


router = APIRouter(prefix="/eda", tags=["eda"])


@router.post("/datasets/{dataset_id}/analyze", response_model=EDAReportRead)
def analyze_dataset(
    dataset_id: int,
    target_column: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return eda_service.analyze_dataset(db, dataset_id, target_column)


@router.get("/datasets/{dataset_id}/latest", response_model=EDAReportRead | None)
def get_latest_eda_report(dataset_id: int, db: Session = Depends(get_db)):
    return eda_service.get_latest_report(db, dataset_id)


@router.get("/reports/{report_id}/download")
def download_eda_report(report_id: int, db: Session = Depends(get_db)):
    report = eda_service.get_report_or_404(db, report_id)
    return FileResponse(
        report.report_path,
        media_type="text/html",
        filename=f"eda_report_dataset_{report.dataset_id}.html",
    )
