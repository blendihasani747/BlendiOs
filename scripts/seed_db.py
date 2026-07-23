"""Initialize the BlendiOS SQLite database with schema and seed data."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow imports from src when running script directly
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from blendios.common.paths import ensure_data_dirs
from blendios.database.connection import DatabaseConnection


def main() -> int:
    """Seed the database."""
    ensure_data_dirs()

    schema_path = project_root / "docs" / "Database_Schema.sql"
    if not schema_path.exists():
        print(f"Schema file not found: {schema_path}")
        return 1

    schema = schema_path.read_text(encoding="utf-8")
    db = DatabaseConnection()
    db.execute_script(schema)
    print(f"Database initialized at: {db.db_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
