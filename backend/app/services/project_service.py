from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_project(db: Session, project_data: ProjectCreate) -> Project:
    project = Project(
        name=project_data.name,
        description=project_data.description,
    )
    db.add(project)
    db.flush()
    log_activity(db, project.id, "Project Created", f"Project '{project.name}' was created.")
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session) -> list[Project]:
    return list(db.scalars(select(Project).order_by(Project.created_at.desc())))


def get_project_or_404(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )
    return project


def update_project(db: Session, project_id: int, project_data: ProjectUpdate) -> Project:
    project = get_project_or_404(db, project_id)
    changes = project_data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(project, field, value)

    project.updated_at = datetime.utcnow()
    log_activity(db, project.id, "Project Updated", f"Project '{project.name}' was updated.")
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int) -> None:
    project = get_project_or_404(db, project_id)
    db.delete(project)
    db.commit()


def log_activity(db: Session, project_id: int, activity_type: str, message: str | None = None) -> Activity:
    activity = Activity(
        project_id=project_id,
        activity_type=activity_type,
        message=message,
    )
    db.add(activity)
    return activity
