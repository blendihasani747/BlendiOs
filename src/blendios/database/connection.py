"""SQLite connection management."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from blendios.constants import DEFAULT_DB_PATH


class DatabaseConnection:
    """Manages SQLite connection lifecycle."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path).expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self):
        """Yield a SQLite connection with foreign keys enabled."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_script(self, script: str) -> None:
        """Execute a SQL script."""
        with self.connect() as conn:
            conn.executescript(script)
