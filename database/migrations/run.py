import sqlite3
import os
from pathlib import Path

from database.create_consultation_tables import (
    create_consultation_tables,
)
from database.migrations.add_reference_image_blob_name import (
    add_reference_image_blob_name,
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = Path(
    os.getenv(
        "APP_DB_PATH",
        str(BASE_DIR / "data" / "app.db"),
    )
)


def verify_schema():
    conn = sqlite3.connect(DB_PATH)

    try:
        columns = conn.execute(
            "PRAGMA table_info(consultations)"
        ).fetchall()

        column_names = {
            column[1]
            for column in columns
        }

        if "reference_image_blob_name" not in column_names:
            raise RuntimeError(
                "reference_image_blob_name 컬럼이 없습니다."
            )

        print("DB schema 검증 완료")

    finally:
        conn.close()


def run_migrations():
    print(f"DB 경로: {DB_PATH}")

    create_consultation_tables()

    add_reference_image_blob_name()

    verify_schema()

    print("DB migration 완료")


if __name__ == "__main__":
    run_migrations()