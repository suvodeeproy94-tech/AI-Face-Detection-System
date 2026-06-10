"""
This file handles the local SQLite database.

The database is used only for simple detection history and statistics.
It keeps the project professional without making the setup difficult.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from config import DATABASE_PATH


def prepare_database_folder() -> None:
    """Create the data folder if it does not exist."""

    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)


def get_database_connection() -> sqlite3.Connection:
    """Create one SQLite connection and return rows as dictionary-like data."""

    prepare_database_folder()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def setup_database() -> None:
    """Create the detection table when the app starts."""

    connection = get_database_connection()

    with connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS detection_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,
                face_count INTEGER NOT NULL,
                average_confidence REAL NOT NULL,
                processing_time_ms REAL NOT NULL,
                model_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

    connection.close()


def save_detection_record(
    source_type: str,
    face_count: int,
    average_confidence: float,
    processing_time_ms: float,
    model_name: str,
) -> None:
    """Save one detection result in SQLite."""

    created_at = datetime.now(timezone.utc).isoformat()
    connection = get_database_connection()

    with connection:
        connection.execute(
            """
            INSERT INTO detection_records (
                source_type,
                face_count,
                average_confidence,
                processing_time_ms,
                model_name,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                source_type,
                face_count,
                average_confidence,
                processing_time_ms,
                model_name,
                created_at,
            ),
        )

    connection.close()


def get_recent_detection_records(limit: int = 20) -> list[dict]:
    """Return the latest detection records for the dashboard."""

    connection = get_database_connection()
    rows = connection.execute(
        """
        SELECT
            id,
            source_type,
            face_count,
            average_confidence,
            processing_time_ms,
            model_name,
            created_at
        FROM detection_records
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    connection.close()

    return [dict(row) for row in rows]


def get_detection_summary() -> dict:
    """Calculate simple summary numbers for the live dashboard."""

    connection = get_database_connection()
    row = connection.execute(
        """
        SELECT
            COUNT(*) AS total_frames,
            COALESCE(SUM(face_count), 0) AS total_faces,
            COALESCE(AVG(average_confidence), 0) AS average_confidence,
            COALESCE(AVG(processing_time_ms), 0) AS average_processing_time_ms,
            COALESCE(MAX(face_count), 0) AS highest_face_count
        FROM detection_records
        """
    ).fetchone()
    connection.close()

    return {
        "total_frames": int(row["total_frames"]),
        "total_faces": int(row["total_faces"]),
        "average_confidence": round(float(row["average_confidence"]), 2),
        "average_processing_time_ms": round(
            float(row["average_processing_time_ms"]),
            2,
        ),
        "highest_face_count": int(row["highest_face_count"]),
    }


def clear_detection_records() -> None:
    """Delete old detection records when the user resets the dashboard."""

    connection = get_database_connection()

    with connection:
        connection.execute("DELETE FROM detection_records")

    connection.close()
