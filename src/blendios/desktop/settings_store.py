"""Persistent desktop settings storage for BlendiOS."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from blendios.constants import DEFAULT_DATA_DIR


@dataclass(slots=True)
class DesktopSettings:
    """Serializable user-facing desktop preferences."""

    theme: str = "dark"
    accent_color: str = "#3a86ff"
    taskbar_position: str = "bottom"
    taskbar_auto_hide: bool = False
    animation_speed: str = "normal"
    wallpaper_category: str = "Dark"
    wallpaper_slideshow: bool = True
    wallpaper_interval_sec: int = 20
    icon_size: str = "medium"
    notifications_enabled: bool = True
    wifi_enabled: bool = True
    bluetooth_enabled: bool = False
    night_mode_enabled: bool = False
    brightness: int = 80
    volume: int = 65
    lock_password: str = "blendios"
    security_encryption_enabled: bool = False
    proxy_url: str = ""


class SettingsStore:
    """Small JSON-backed settings repository."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or (DEFAULT_DATA_DIR / "system" / "ui_settings.json")
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> DesktopSettings:
        if not self._path.exists():
            settings = DesktopSettings()
            self.save(settings)
            return settings

        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            return DesktopSettings(**payload)
        except (json.JSONDecodeError, OSError, TypeError):
            # Fall back to defaults if file is malformed or unreadable.
            settings = DesktopSettings()
            self.save(settings)
            return settings

    def save(self, settings: DesktopSettings) -> None:
        self._path.write_text(
            json.dumps(asdict(settings), indent=2),
            encoding="utf-8",
        )

    def update(self, **changes: Any) -> DesktopSettings:
        settings = self.load()
        for key, value in changes.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        self.save(settings)
        return settings
