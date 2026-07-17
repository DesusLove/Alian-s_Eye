"""Persistent scan history backed by SQLite."""

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from platformdirs import user_data_dir

_HISTORY_DIR = Path(user_data_dir("alians_eye", ensure_exists=True))
_DB_PATH = _HISTORY_DIR / "history.db"


class HistoryDB:
    def __init__(self, db_path: Path = _DB_PATH) -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    username TEXT NOT NULL,
                    scan_level TEXT NOT NULL,
                    total_found INTEGER DEFAULT 0,
                    total_scanned INTEGER DEFAULT 0,
                    results_json TEXT,
                    UNIQUE(timestamp, username)
                )
            """)

    def save_scan(
        self,
        username: str,
        scan_level: str,
        all_results: dict[str, list[dict[str, Any]]],
        total_found: int = 0,
    ) -> None:
        total_scanned = sum(len(r) for r in all_results.values())
        with sqlite3.connect(self.db_path) as con:
            con.execute(
                "INSERT OR REPLACE INTO scans (timestamp, username, scan_level, total_found, total_scanned, results_json) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    time.time(),
                    username,
                    scan_level,
                    total_found,
                    total_scanned,
                    json.dumps(all_results, default=str),
                ),
            )

    def recent_scans(self, limit: int = 20) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as con:
            con.row_factory = sqlite3.Row
            rows = con.execute(
                "SELECT id, timestamp, username, scan_level, total_found, total_scanned "
                "FROM scans ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "id": r["id"],
                "timestamp": r["timestamp"],
                "username": r["username"],
                "scan_level": r["scan_level"],
                "total_found": r["total_found"],
                "total_scanned": r["total_scanned"],
            }
            for r in rows
        ]

    def get_scan(self, scan_id: int) -> dict[str, Any] | None:
        with sqlite3.connect(self.db_path) as con:
            con.row_factory = sqlite3.Row
            row = con.execute(
                "SELECT * FROM scans WHERE id = ?", (scan_id,)
            ).fetchone()
        if row is None:
            return None
        return dict(row)

    def delete_scan(self, scan_id: int) -> None:
        with sqlite3.connect(self.db_path) as con:
            con.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
