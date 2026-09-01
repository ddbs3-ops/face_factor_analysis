import sqlite3
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

def create_consultation_tables():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            share_id TEXT NOT NULL UNIQUE,
            summary TEXT NOT NULL,
            consultation_text TEXT NOT NULL,
            personal_request TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS consultation_key_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consultation_id INTEGER NOT NULL,
            element TEXT NOT NULL,
            score INTEGER NOT NULL,
            text TEXT NOT NULL,
            display_order INTEGER NOT NULL,

            FOREIGN KEY (consultation_id)
                REFERENCES consultations(id)
                ON DELETE CASCADE
        )
        """
    )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_consultation_tables()