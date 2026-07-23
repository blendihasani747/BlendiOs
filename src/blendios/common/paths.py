"""Path helpers for BlendiOS."""

from __future__ import annotations

from pathlib import Path

from blendios.constants import (
    DEFAULT_DATA_DIR,
    DEFAULT_DB_PATH,
    DEFAULT_LOG_PATH,
    DEFAULT_PLUGINS_PATH,
    DEFAULT_VFS_PATH,
)


def resolve_path(path: str | Path) -> Path:
    """Resolve a path, expanding user home and environment variables."""
    return Path(path).expanduser().resolve()


def blendios_downloads_dir() -> Path:
    """Return the BlendiOS-local downloads directory."""
    downloads = DEFAULT_VFS_PATH / "Downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    return downloads


def ensure_data_dirs() -> None:
    """Create default BlendiOS data directories if they do not exist."""
    dirs = [
        DEFAULT_DATA_DIR,
        DEFAULT_DATA_DIR / "system",
        DEFAULT_DB_PATH.parent,
        DEFAULT_VFS_PATH,
        DEFAULT_VFS_PATH / "Downloads",
        DEFAULT_PLUGINS_PATH,
        DEFAULT_LOG_PATH,
    ]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
