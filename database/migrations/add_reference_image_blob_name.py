import sqlite3
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = Path(
    os.getenv(
        "APP_DB_PATH",
        str(BASE_DIR / "data" / "app.db"),
    )
)


def add_reference_image_blob_name():
    conn = sqlite3.connect(DB_PATH)

    try:
        columns = conn.execute(
            "PRAGMA table_info(consultations)"
        ).fetchall()

        column_names = {
            column[1]
            for column in columns
        }

        if "reference_image_blob_name" in column_names:
            print("이미 컬럼이 존재합니다.")
            return

        conn.execute(
            """
            ALTER TABLE consultations
            ADD COLUMN reference_image_blob_name TEXT
            """
        )

        conn.commit()

        print("reference_image_blob_name 컬럼 추가 완료")

    finally:
        conn.close()

if __name__ == "__main__":
    add_reference_image_blob_name()