from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class FeatureReport(Base):
    __tablename__ = "feature_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False, index=True)
    engineered_dataset_path: Mapped[str] = mapped_column(String(500), nullable=False)
    report_path: Mapped[str] = mapped_column(String(500), nullable=False)
    report_json_path: Mapped[str] = mapped_column(String(500), nullable=False)
    feature_summary: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    original_columns: Mapped[int] = mapped_column(Integer, nullable=False)
    final_columns: Mapped[int] = mapped_column(Integer, nullable=False)
    encoding_method: Mapped[str] = mapped_column(String(100), nullable=False)
    scaling_method: Mapped[str] = mapped_column(String(100), nullable=False)
    features_created: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    dropped_columns: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    target_column: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="feature_reports")
    dataset: Mapped["Dataset"] = relationship(back_populates="feature_reports")
