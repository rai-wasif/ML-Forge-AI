from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TrainingReport(Base):
    __tablename__ = "training_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False, index=True)
    problem_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_column: Mapped[str] = mapped_column(String(255), nullable=False)
    selected_models: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    best_model: Mapped[str] = mapped_column(String(255), nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    training_time: Mapped[float] = mapped_column(Float, nullable=False)
    model_path: Mapped[str] = mapped_column(String(500), nullable=False)
    report_path: Mapped[str] = mapped_column(String(500), nullable=False)
    report_json_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mlflow_run_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mlflow_experiment_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mlflow_artifact_uri: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    shap_summary_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    shap_importance_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    final_report_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    artifacts: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="training_reports")
    dataset: Mapped["Dataset"] = relationship(back_populates="training_reports")
