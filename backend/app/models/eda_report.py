from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class EDAReport(Base):
    __tablename__ = "eda_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False, index=True)
    report_path: Mapped[str] = mapped_column(String(500), nullable=False)
    report_json_path: Mapped[str] = mapped_column(String(500), nullable=False)
    report_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    visualizations: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="eda_reports")
    dataset: Mapped["Dataset"] = relationship(back_populates="eda_reports")
