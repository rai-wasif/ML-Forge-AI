from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    column_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    column_names: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    data_types: Mapped[dict[str, str]] = mapped_column(JSON, default=dict, nullable=False)
    missing_values: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    missing_values_by_column: Mapped[dict[str, int]] = mapped_column(JSON, default=dict, nullable=False)
    duplicate_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    memory_usage_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="datasets")
    eda_reports: Mapped[list["EDAReport"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    cleaning_reports: Mapped[list["CleaningReport"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
