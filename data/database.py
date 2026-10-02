import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from config import DATABASE_PATH


@contextmanager
def database_connection(
    path: str | Path = DATABASE_PATH,
) -> Iterator[sqlite3.Connection]:
    database_path = Path(path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(database_path), timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database(path: str | Path = DATABASE_PATH) -> None:
    with database_connection(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                scan_id TEXT PRIMARY KEY,
                scanned_at TEXT NOT NULL,
                crop TEXT NOT NULL,
                class_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                confidence_status TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id TEXT PRIMARY KEY,
                scan_id TEXT NOT NULL UNIQUE REFERENCES scans(scan_id),
                rating TEXT NOT NULL CHECK (
                    rating IN ('Helpful', 'Not helpful', 'Not sure')
                ),
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS scans_scanned_at_idx "
            "ON scans(scanned_at DESC)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS feedback_status_idx ON feedback(status)"
        )