from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    datasets: Mapped[list["Dataset"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list["Activity"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    eda_reports: Mapped[list["EDAReport"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    cleaning_reports: Mapped[list["CleaningReport"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    feature_reports: Mapped[list["FeatureReport"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    training_reports: Mapped[list["TrainingReport"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
