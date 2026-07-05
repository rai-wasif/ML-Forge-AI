from sqlalchemy import text

from app.database.base import Base
from app.database.session import engine
from app.models import activity, dataset, eda_report, project  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_dataset_metadata_columns()


def ensure_dataset_metadata_columns() -> None:
    statements = [
        "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS file_type VARCHAR(20)",
        "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS file_size_bytes INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS row_count INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS column_count INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS column_names JSON NOT NULL DEFAULT '[]'::json",
        "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS data_types JSON NOT NULL DEFAULT '{}'::json",
        "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS missing_values INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS missing_values_by_column JSON NOT NULL DEFAULT '{}'::json",
        "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS duplicate_rows INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE datasets ADD COLUMN IF NOT EXISTS memory_usage_bytes INTEGER NOT NULL DEFAULT 0",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
