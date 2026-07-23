"""Wallpaper and slideshow manager for BlendiOS desktop."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal


class WallpaperManager(QObject):
    """Manages wallpaper categories and slideshow progression."""

    wallpaper_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._wallpapers = {
            "Nature": [
                "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #4a8d66, stop:1 #162f27)",
                "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #6fa37b, stop:1 #24422e)",
            ],
            "Abstract": [
                "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1f2f60, stop:1 #4e2e8a)",
                "qradialgradient(cx:0.5, cy:0.5, radius:0.9, stop:0 #2f4fa5, stop:1 #0f1429)",
            ],
            "Dark": [
                "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #121620, stop:1 #05070d)",
                "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #171f30, stop:1 #0a0f18)",
            ],
            "Light": [
                "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #f4f8ff, stop:1 #d5e8ff)",
                "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ffffff, stop:1 #e9f0fa)",
            ],
            "Minimal": [
                "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #2b3448, stop:1 #1b2230)",
                "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1c1f2b, stop:1 #11141b)",
            ],
        }
        self._category = "Dark"
        self._index = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.next_wallpaper)
        self._custom_images: list[str] = []

    def categories(self) -> list[str]:
        return sorted(self._wallpapers.keys())

    def set_category(self, name: str) -> None:
        if name not in self._wallpapers:
            return
        self._category = name
        self._index = 0
        self.wallpaper_changed.emit(self.current_wallpaper())

    def add_custom_image(self, image_path: str) -> bool:
        """Add a user-selected image wallpaper under Custom category."""
        path = Path(image_path)
        if not path.exists():
            return False

        as_uri = f"image:{path.as_posix()}"
        if as_uri not in self._custom_images:
            self._custom_images.append(as_uri)
            self._wallpapers.setdefault("Custom", []).append(as_uri)

        self._category = "Custom"
        self._index = max(len(self._wallpapers["Custom"]) - 1, 0)
        self.wallpaper_changed.emit(self.current_wallpaper())
        return True

    def start_slideshow(self, interval_sec: int) -> None:
        self._timer.start(max(5, interval_sec) * 1000)

    def stop_slideshow(self) -> None:
        self._timer.stop()

    def current_wallpaper(self) -> str:
        items = self._wallpapers[self._category]
        return items[self._index % len(items)]

    def next_wallpaper(self) -> None:
        items = self._wallpapers[self._category]
        self._index = (self._index + 1) % len(items)
        self.wallpaper_changed.emit(items[self._index])

    def cycle_wallpapers(self, category: str) -> Iterator[str]:
        self.set_category(category)
        while True:
            yield self.current_wallpaper()
            self.next_wallpaper()
