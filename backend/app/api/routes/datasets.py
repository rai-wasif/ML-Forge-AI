from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.dataset import DatasetRead
from app.services import dataset_service


router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/upload", response_model=DatasetRead, status_code=status.HTTP_201_CREATED)
def upload_dataset(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return dataset_service.upload_dataset(db, project_id, file)


@router.get("/project/{project_id}", response_model=list[DatasetRead])
def list_project_datasets(project_id: int, db: Session = Depends(get_db)):
    return dataset_service.list_project_datasets(db, project_id)
