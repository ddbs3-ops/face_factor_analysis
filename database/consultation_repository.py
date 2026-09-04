import sqlite3
import uuid
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(
    os.getenv(
        "APP_DB_PATH",
        str(BASE_DIR / "data" / "app.db"),
    )
)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    
def save_consultation(
    summary: str,
    consultation_text: str,
    key_requests: list[dict],
    personal_request: str | None = None,
    reference_image_blob_name: str | None = None,
) -> str:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        share_id = uuid.uuid4().hex

        cursor = conn.execute(
            """
            INSERT INTO consultations (
                share_id,
                summary,
                consultation_text,
                personal_request,
                reference_image_blob_name
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                share_id,
                summary,
                consultation_text,
                personal_request,
                reference_image_blob_name
            ),
        )

        consultation_id = cursor.lastrowid

        for order, key_request in enumerate(key_requests):
            conn.execute(
                """
                INSERT INTO consultation_key_requests (
                    consultation_id,
                    element,
                    score,
                    text,
                    display_order
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    consultation_id,
                    key_request["element"],
                    key_request["score"],
                    key_request["text"],
                    order,
                ),
            )

        conn.commit()

        return share_id

    except:
        conn.rollback()
        raise

    finally:
        conn.close()

def get_consultation_by_share_id(share_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        consultation = conn.execute(
            """
            SELECT
                id,
                share_id,
                summary,
                consultation_text,
                personal_request,
                reference_image_blob_name,
                created_at,
                expires_at
            FROM consultations
            WHERE share_id = ?
            """,
            (share_id,),
        ).fetchone()

        if consultation is None:
            return None

        key_requests = conn.execute(
            """
            SELECT
                element,
                score,
                text,
                display_order
            FROM consultation_key_requests
            WHERE consultation_id = ?
            ORDER BY display_order ASC
            """,
            (consultation["id"],),
        ).fetchall()

        return {
            "share_id": consultation["share_id"],
            "summary": consultation["summary"],
            "consultation_text": consultation["consultation_text"],
            "personal_request": consultation["personal_request"],
            "reference_image_blob_name": consultation["reference_image_blob_name"],
            "created_at": consultation["created_at"],
            "expires_at": consultation["expires_at"],
            "key_requests": [
                {
                    "element": row["element"],
                    "score": row["score"],
                    "text": row["text"],
                }
                for row in key_requests
            ],
        }

    finally:
        conn.close()
