import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from config import DATABASE_PATH
from data.database import database_connection


@dataclass(frozen=True)
class ScanRecord:
    scan_id: str
    scanned_at: str
    crop: str
    class_name: str
    confidence: float
    confidence_status: str


def save_scan(
    crop: str,
    class_name: str,
    confidence: float,
    confidence_status: str,
    path: str | Path = DATABASE_PATH,
) -> ScanRecord:
    record = ScanRecord(
        scan_id=str(uuid4()),
        scanned_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        crop=crop,
        class_name=class_name,
        confidence=float(confidence),
        confidence_status=confidence_status,
    )
    with database_connection(path) as connection:
        connection.execute(
            """
            INSERT INTO scans (
                scan_id, scanned_at, crop, class_name, confidence, confidence_status
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record.scan_id,
                record.scanned_at,
                record.crop,
                record.class_name,
                record.confidence,
                record.confidence_status,
            ),
        )
    return record


def recent_scans(
    limit: int = 100,
    path: str | Path = DATABASE_PATH,
) -> tuple[ScanRecord, ...]:
    safe_limit = min(max(int(limit), 1), 500)
    with database_connection(path) as connection:
        rows = connection.execute(
            """
            SELECT scan_id, scanned_at, crop, class_name, confidence,
                   confidence_status
            FROM scans
            ORDER BY scanned_at DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
    return tuple(ScanRecord(**dict(row)) for row in rows)


def get_scan(scan_id: str, path: str | Path = DATABASE_PATH) -> ScanRecord | None:
    with database_connection(path) as connection:
        row = connection.execute(
            """
            SELECT scan_id, scanned_at, crop, class_name, confidence,
                   confidence_status
            FROM scans WHERE scan_id = ?
            """,
            (scan_id,),
        ).fetchone()
    return ScanRecord(**dict(row)) if row is not None else None