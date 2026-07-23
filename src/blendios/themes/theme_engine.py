"""Theme engine for BlendiOS desktop UI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication


@dataclass(slots=True)
class ThemeSpec:
    """Strongly-typed theme definition."""

    name: str
    background: str
    surface: str
    surface_alt: str
    primary: str
    secondary: str
    text: str
    text_muted: str
    border: str
    shadow: str
    font_family: str
    font_size: int
    radius: int


class ThemeEngine(QObject):
    """Centralized theme and stylesheet management."""

    theme_changed = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        self._themes: dict[str, ThemeSpec] = self._build_themes()
        self._active_theme = "dark"

    @property
    def active_theme_name(self) -> str:
        return self._active_theme

    def theme_names(self) -> list[str]:
        return sorted(self._themes.keys())

    def get_theme(self, name: str | None = None) -> ThemeSpec:
        theme_name = name or self._active_theme
        return self._themes.get(theme_name, self._themes["dark"])

    def set_theme(self, name: str) -> ThemeSpec:
        if name not in self._themes:
            name = "dark"
        self._active_theme = name
        theme = self.get_theme()
        self.theme_changed.emit(self.theme_to_dict(theme))
        return theme

    def apply_to_application(self, app: QApplication) -> None:
        """Apply the active QSS theme to the whole application."""
        theme = self.get_theme()
        app.setStyleSheet(self._build_qss(theme))

    def theme_to_dict(self, theme: ThemeSpec | None = None) -> dict[str, Any]:
        source = theme or self.get_theme()
        return {
            "name": source.name,
            "background": source.background,
            "surface": source.surface,
            "surface_alt": source.surface_alt,
            "primary": source.primary,
            "secondary": source.secondary,
            "text": source.text,
            "text_muted": source.text_muted,
            "border": source.border,
            "shadow": source.shadow,
            "font_family": source.font_family,
            "font_size": source.font_size,
            "radius": source.radius,
        }

    def _build_themes(self) -> dict[str, ThemeSpec]:
        return {
            "dark": ThemeSpec(
                name="dark",
                background="#0f1218",
                surface="#1b2230",
                surface_alt="#232d40",
                primary="#3a86ff",
                secondary="#00c2a8",
                text="#eff3ff",
                text_muted="#a8b3c7",
                border="#33415b",
                shadow="rgba(10, 14, 24, 0.48)",
                font_family="Segoe UI",
                font_size=13,
                radius=12,
            ),
            "light": ThemeSpec(
                name="light",
                background="#f2f6fc",
                surface="#ffffff",
                surface_alt="#edf2fb",
                primary="#0063d1",
                secondary="#0f766e",
                text="#132238",
                text_muted="#4c5e78",
                border="#ccd7e8",
                shadow="rgba(30, 52, 86, 0.18)",
                font_family="Segoe UI",
                font_size=13,
                radius=12,
            ),
            "blue": ThemeSpec(
                name="blue",
                background="#0c1931",
                surface="#13284d",
                surface_alt="#1a3563",
                primary="#68a5ff",
                secondary="#52d1ff",
                text="#ecf3ff",
                text_muted="#afc3e7",
                border="#2f4f82",
                shadow="rgba(8, 20, 44, 0.45)",
                font_family="Segoe UI",
                font_size=13,
                radius=12,
            ),
            "green": ThemeSpec(
                name="green",
                background="#0d1e1a",
                surface="#163029",
                surface_alt="#1d3c34",
                primary="#48bf84",
                secondary="#8ddf6e",
                text="#ebfbf4",
                text_muted="#b5d6c8",
                border="#2f5547",
                shadow="rgba(7, 25, 20, 0.44)",
                font_family="Segoe UI",
                font_size=13,
                radius=12,
            ),
            "purple": ThemeSpec(
                name="purple",
                background="#1a1326",
                surface="#2a1f3f",
                surface_alt="#372952",
                primary="#9b8cff",
                secondary="#5eead4",
                text="#f7f3ff",
                text_muted="#cbbde7",
                border="#4a3b67",
                shadow="rgba(16, 10, 30, 0.44)",
                font_family="Segoe UI",
                font_size=13,
                radius=12,
            ),
        }

    def _build_qss(self, theme: ThemeSpec) -> str:
        """Generate global QSS from theme tokens."""
        return f"""
            * {{
                font-family: '{theme.font_family}';
                font-size: {theme.font_size}px;
                color: {theme.text};
            }}

            QWidget {{
                background-color: {theme.background};
                color: {theme.text};
            }}

            QFrame#surface,
            QWidget#surface {{
                background-color: {theme.surface};
                border: 1px solid {theme.border};
                border-radius: {theme.radius}px;
            }}

            QMainWindow {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme.background},
                    stop:1 {theme.surface}
                );
            }}

            QWidget#taskbar {{
                background-color: rgba(20, 26, 38, 0.82);
                border: 1px solid {theme.border};
                border-radius: {theme.radius}px;
            }}

            QFrame#startMenu,
            QFrame#quickPanel {{
                background-color: rgba(20, 26, 38, 0.92);
                border: 1px solid {theme.border};
                border-radius: {theme.radius}px;
            }}

            QFrame#lockOverlay {{
                background-color: rgba(8, 12, 20, 0.78);
                border: none;
            }}

            QListWidget#desktopShortcuts {{
                background: transparent;
                border: none;
                outline: none;
            }}

            QListWidget#desktopShortcuts::item {{
                border: 1px solid transparent;
                border-radius: {theme.radius}px;
                padding: 8px;
                margin: 4px;
            }}

            QListWidget#desktopShortcuts::item:hover {{
                background-color: rgba(255, 255, 255, 0.10);
                border-color: rgba(255, 255, 255, 0.16);
            }}

            QListWidget#desktopShortcuts::item:selected {{
                background-color: rgba(58, 134, 255, 0.32);
                border-color: {theme.primary};
            }}

            QPushButton {{
                background-color: {theme.surface_alt};
                border: 1px solid {theme.border};
                border-radius: {theme.radius - 2}px;
                padding: 9px 13px;
                color: {theme.text};
            }}

            QPushButton:hover {{
                border-color: {theme.primary};
                background-color: rgba(58, 134, 255, 0.18);
            }}

            QPushButton:pressed {{
                background-color: {theme.primary};
                color: {theme.text};
            }}

            QToolButton {{
                background-color: rgba(255, 255, 255, 0.04);
                border: 1px solid {theme.border};
                border-radius: {theme.radius - 4}px;
                padding: 4px;
            }}

            QToolButton:hover {{
                border-color: {theme.primary};
                background-color: rgba(58, 134, 255, 0.18);
            }}

            QLineEdit,
            QTextEdit,
            QListWidget,
            QTreeView,
            QTableView {{
                background-color: rgba(14, 19, 29, 0.78);
                border: 1px solid {theme.border};
                border-radius: {theme.radius - 2}px;
                padding: 8px;
                selection-background-color: {theme.primary};
                selection-color: {theme.text};
            }}

            QSlider::groove:horizontal {{
                height: 6px;
                border-radius: 3px;
                background: {theme.surface_alt};
                border: 1px solid {theme.border};
            }}

            QSlider::handle:horizontal {{
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
                border: 1px solid {theme.primary};
                background: {theme.primary};
            }}

            QFrame#windowTitleBar,
            QWidget#windowTitleBar {{
                background-color: rgba(23, 31, 44, 0.92);
                border-bottom: 1px solid {theme.border};
                border-top-left-radius: {theme.radius}px;
                border-top-right-radius: {theme.radius}px;
            }}

            QFrame#windowContent,
            QWidget#windowContent {{
                background-color: {theme.surface};
                border-bottom-left-radius: {theme.radius}px;
                border-bottom-right-radius: {theme.radius}px;
            }}

            QPushButton#windowClose:hover {{
                border-color: #ff5f56;
                background-color: rgba(255, 95, 86, 0.25);
            }}

            QLabel#caption {{
                color: {theme.text_muted};
            }}
        """
