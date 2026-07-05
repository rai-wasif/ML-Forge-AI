from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.features import FeatureReportRead
from app.services import feature_service


router = APIRouter(prefix="/features", tags=["features"])


@router.post("/datasets/{dataset_id}/generate", response_model=FeatureReportRead)
def generate_features(
    dataset_id: int,
    target_column: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return feature_service.generate_features(db, dataset_id, target_column)


@router.get("/datasets/{dataset_id}/latest", response_model=FeatureReportRead | None)
def get_latest_feature_report(dataset_id: int, db: Session = Depends(get_db)):
    return feature_service.get_latest_report(db, dataset_id)


@router.get("/reports/{report_id}/download")
def download_feature_report(report_id: int, db: Session = Depends(get_db)):
    report = feature_service.get_report_or_404(db, report_id)
    return FileResponse(
        report.report_path,
        media_type="text/html",
        filename=f"feature_report_dataset_{report.dataset_id}.html",
    )


@router.get("/datasets/{dataset_id}/download")
def download_engineered_dataset(dataset_id: int, db: Session = Depends(get_db)):
    report = feature_service.get_latest_report(db, dataset_id)
    if report is None:
        report = feature_service.raise_report_not_found()
    return FileResponse(
        report.engineered_dataset_path,
        media_type="application/octet-stream",
        filename=f"feature_dataset_{dataset_id}.parquet",
    )
