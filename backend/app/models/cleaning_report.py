from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CleaningReport(Base):
    __tablename__ = "cleaning_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False, index=True)
    cleaned_dataset_path: Mapped[str] = mapped_column(String(500), nullable=False)
    report_path: Mapped[str] = mapped_column(String(500), nullable=False)
    report_json_path: Mapped[str] = mapped_column(String(500), nullable=False)
    cleaning_summary: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    original_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    final_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    original_columns: Mapped[int] = mapped_column(Integer, nullable=False)
    final_columns: Mapped[int] = mapped_column(Integer, nullable=False)
    missing_values_before: Mapped[int] = mapped_column(Integer, nullable=False)
    missing_values_after: Mapped[int] = mapped_column(Integer, nullable=False)
    duplicates_removed: Mapped[int] = mapped_column(Integer, nullable=False)
    outliers_handled: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="cleaning_reports")
    dataset: Mapped["Dataset"] = relationship(back_populates="cleaning_reports")
