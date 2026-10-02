import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from config import DATABASE_PATH
from data.database import database_connection


FEEDBACK_RATINGS = ("Helpful", "Not helpful", "Not sure")
MAX_NOTE_LENGTH = 1000


@dataclass(frozen=True)
class FeedbackRecord:
    feedback_id: str
    scan_id: str
    rating: str
    note: str
    created_at: str
    status: str


def save_feedback(
    scan_id: str,
    rating: str,
    note: str = "",
    path: str | Path = DATABASE_PATH,
) -> FeedbackRecord:
    if rating not in FEEDBACK_RATINGS:
        raise ValueError("Choose one of the available feedback options.")

    cleaned_note = note.strip()[:MAX_NOTE_LENGTH]
    feedback_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with database_connection(path) as connection:
        connection.execute(
            """
            INSERT INTO feedback (
                feedback_id, scan_id, rating, note, created_at, status
            ) VALUES (?, ?, ?, ?, ?, 'pending')
            ON CONFLICT(scan_id) DO UPDATE SET
                rating = excluded.rating,
                note = excluded.note,
                created_at = excluded.created_at,
                status = 'pending'
            """,
            (feedback_id, scan_id, rating, cleaned_note, created_at),
        )
        row = connection.execute(
            """
            SELECT feedback_id, scan_id, rating, note, created_at, status
            FROM feedback WHERE scan_id = ?
            """,
            (scan_id,),
        ).fetchone()
    if row is None:
        raise sqlite3.DatabaseError("Feedback could not be saved.")
    return FeedbackRecord(**dict(row))


def pending_feedback(
    limit: int = 100,
    path: str | Path = DATABASE_PATH,
) -> tuple[FeedbackRecord, ...]:
    safe_limit = min(max(int(limit), 1), 500)
    with database_connection(path) as connection:
        rows = connection.execute(
            """
            SELECT feedback_id, scan_id, rating, note, created_at, status
            FROM feedback WHERE status = 'pending'
            ORDER BY created_at DESC LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
    return tuple(FeedbackRecord(**dict(row)) for row in rows)