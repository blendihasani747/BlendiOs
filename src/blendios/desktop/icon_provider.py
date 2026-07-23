"""Premium icon provider utilities for BlendiOS desktop UI."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QStyle


@dataclass(frozen=True, slots=True)
class GlyphSpec:
    """Visual token for generated app icons."""

    glyph: str
    start: str
    end: str


_GLYPH_MAP: dict[str, GlyphSpec] = {
    "terminal": GlyphSpec(glyph=">_", start="#6ee7ff", end="#2b70ff"),
    "calculator": GlyphSpec(glyph="+", start="#ffcf7a", end="#ff8d4d"),
    "browser": GlyphSpec(glyph="◎", start="#7ac6ff", end="#3a86ff"),
    "file_explorer": GlyphSpec(glyph="▣", start="#7fe8b8", end="#33b07a"),
    "notes": GlyphSpec(glyph="✎", start="#f7a2d0", end="#d166b2"),
    "settings": GlyphSpec(glyph="⚙", start="#d8dff2", end="#8ea3c8"),
}


def get_app_icon(style: QStyle, app_id: str, size: int = 28) -> QIcon:
    """Return a premium generated icon for an app id."""
    spec = _GLYPH_MAP.get(app_id)
    if spec is None:
        return style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)
    return _build_icon(spec, size)


def _build_icon(spec: GlyphSpec, size: int) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    rect = QRect(0, 0, size, size)
    base_rect = rect.adjusted(1, 1, -1, -1)

    gradient = QLinearGradient(base_rect.topLeft(), base_rect.bottomRight())
    gradient.setColorAt(0.0, QColor(spec.start))
    gradient.setColorAt(1.0, QColor(spec.end))

    painter.setPen(QPen(QColor(255, 255, 255, 28), 1))
    painter.setBrush(gradient)
    radius = max(6, int(size * 0.26))
    painter.drawRoundedRect(base_rect, radius, radius)

    font = QFont("Segoe UI", max(9, int(size * 0.36)), QFont.Weight.DemiBold)
    painter.setFont(font)
    painter.setPen(QColor("#f8fbff"))
    painter.drawText(base_rect, Qt.AlignmentFlag.AlignCenter, spec.glyph)

    painter.end()
    return QIcon(pixmap)
