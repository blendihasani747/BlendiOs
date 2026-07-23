"""Managed window wrapper for BlendiOS apps."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEasingCurve, QPoint, Property, QPropertyAnimation, QRect, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


@dataclass(slots=True)
class ResizeState:
    """Tracks active resize edges."""

    left: bool = False
    right: bool = False
    top: bool = False
    bottom: bool = False

    def any_active(self) -> bool:
        """Return True if any resize edge is currently active."""
        return self.left or self.right or self.top or self.bottom


class WindowTitleBar(QWidget):
    """Custom title bar with standard window controls."""

    minimize_requested = Signal()
    maximize_requested = Signal()
    close_requested = Signal()

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("windowTitleBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(38)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(6)

        self.icon_label = QLabel("◼")
        self.icon_label.setFixedWidth(14)
        layout.addWidget(self.icon_label)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(self.title_label)
        layout.addStretch(1)

        self.min_button = QPushButton("-")
        self.max_button = QPushButton("□")
        self.close_button = QPushButton("X")
        self.min_button.setObjectName("windowMin")
        self.max_button.setObjectName("windowMax")
        self.close_button.setObjectName("windowClose")
        for button in (self.min_button, self.max_button, self.close_button):
            button.setFixedSize(30, 28)
            layout.addWidget(button)

        self.min_button.clicked.connect(self.minimize_requested.emit)
        self.max_button.clicked.connect(self.maximize_requested.emit)
        self.close_button.clicked.connect(self.close_requested.emit)

    def set_title(self, title: str) -> None:
        self.title_label.setText(title)


class BaseWindow(QWidget):
    """Reusable frameless base window class for BlendiOS apps."""

    focused = Signal(str)
    minimized = Signal(str)
    closed = Signal(str)

    EDGE_MARGIN = 8

    def __init__(self, window_id: str, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.window_id = window_id
        self._normal_geometry = QRect(0, 0, 920, 620)
        self._drag_active = False
        self._drag_delta = QPoint()
        self._resize_state = ResizeState()
        self._resize_origin = QRect()
        self._resize_start_global = QPoint()
        self._is_maximized = False

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(420, 280)
        self.resize(self._normal_geometry.size())
        self.setObjectName("surface")
        self.setWindowOpacity(0.0)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(34)
        shadow.setOffset(0, 10)
        shadow.setColor(Qt.GlobalColor.black)
        self.setGraphicsEffect(shadow)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(0)

        self.title_bar = WindowTitleBar(title, self)
        self.title_bar.minimize_requested.connect(self.minimize)
        self.title_bar.maximize_requested.connect(self.toggle_maximize)
        self.title_bar.close_requested.connect(self.animate_close)
        self.layout.addWidget(self.title_bar)

        self.content_host = QFrame(self)
        self.content_host.setObjectName("windowContent")
        self.content_host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.content_layout = QVBoxLayout(self.content_host)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.layout.addWidget(self.content_host, 1)

    def set_title(self, title: str) -> None:
        self.title_bar.set_title(title)

    def set_content(self, content: QWidget) -> None:
        while self.content_layout.count():
            existing = self.content_layout.takeAt(0)
            if existing.widget() is not None:
                existing.widget().setParent(None)
        self.content_layout.addWidget(content, 1)

    def animate_open(self) -> None:
        self.show()
        geometry = self.geometry()
        start_rect = QRect(
            geometry.x() + 20,
            geometry.y() + 20,
            max(geometry.width() - 40, self.minimumWidth()),
            max(geometry.height() - 40, self.minimumHeight()),
        )
        geometry_animation = QPropertyAnimation(self, b"geometry", self)
        geometry_animation.setDuration(280)
        geometry_animation.setStartValue(start_rect)
        geometry_animation.setEndValue(geometry)
        geometry_animation.setEasingCurve(QEasingCurve.Type.OutBack)

        opacity_animation = QPropertyAnimation(self, b"windowOpacity", self)
        opacity_animation.setDuration(220)
        opacity_animation.setStartValue(0.0)
        opacity_animation.setEndValue(1.0)
        opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        geometry_animation.start()
        opacity_animation.start()

    def animate_close(self) -> None:
        geometry = self.geometry()
        end_rect = QRect(
            geometry.x() + 14,
            geometry.y() + 20,
            max(geometry.width() - 28, self.minimumWidth()),
            max(geometry.height() - 34, self.minimumHeight()),
        )
        geometry_animation = QPropertyAnimation(self, b"geometry", self)
        geometry_animation.setDuration(220)
        geometry_animation.setStartValue(geometry)
        geometry_animation.setEndValue(end_rect)
        geometry_animation.setEasingCurve(QEasingCurve.Type.InBack)

        opacity_animation = QPropertyAnimation(self, b"windowOpacity", self)
        opacity_animation.setDuration(170)
        opacity_animation.setStartValue(self.windowOpacity())
        opacity_animation.setEndValue(0.0)
        opacity_animation.setEasingCurve(QEasingCurve.Type.InCubic)

        geometry_animation.finished.connect(self.close)
        geometry_animation.start()
        opacity_animation.start()

    def minimize(self) -> None:
        self.showMinimized()
        self.minimized.emit(self.window_id)

    def toggle_maximize(self) -> None:
        if self.parentWidget() is None:
            return

        if self._is_maximized:
            self.setGeometry(self._normal_geometry)
            self._is_maximized = False
            return

        self._normal_geometry = self.geometry()
        parent_rect = self.parentWidget().rect()
        self.setGeometry(parent_rect.adjusted(16, 16, -16, -70))
        self._is_maximized = True

    def mousePressEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self.focused.emit(self.window_id)
        self.raise_()
        self.activateWindow()

        self._resize_state = self._hit_test_resize(event.position().toPoint())
        if self._resize_state.any_active():
            self._resize_origin = self.geometry()
            self._resize_start_global = event.globalPosition().toPoint()
            event.accept()
            return

        if event.position().y() <= self.title_bar.height():
            self._drag_active = True
            self._drag_delta = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        global_pos = event.globalPosition().toPoint()
        if self._resize_state.any_active():
            self._resize_window(global_pos)
            event.accept()
            return

        if self._drag_active and not self._is_maximized:
            self.move(global_pos - self._drag_delta)
            event.accept()
            return

        self._update_resize_cursor(event.position().toPoint())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = False
            self._resize_state = ResizeState()
            self.unsetCursor()
            event.accept()

    def focusInEvent(self, event) -> None:  # type: ignore[override]
        self.focused.emit(self.window_id)
        super().focusInEvent(event)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.closed.emit(self.window_id)
        super().closeEvent(event)

    def _hit_test_resize(self, point: QPoint) -> ResizeState:
        return ResizeState(
            left=point.x() <= self.EDGE_MARGIN,
            right=point.x() >= self.width() - self.EDGE_MARGIN,
            top=point.y() <= self.EDGE_MARGIN,
            bottom=point.y() >= self.height() - self.EDGE_MARGIN,
        )

    def _resize_window(self, global_pos: QPoint) -> None:
        delta = global_pos - self._resize_start_global
        rect = QRect(self._resize_origin)

        if self._resize_state.left:
            rect.setLeft(rect.left() + delta.x())
        if self._resize_state.right:
            rect.setRight(rect.right() + delta.x())
        if self._resize_state.top:
            rect.setTop(rect.top() + delta.y())
        if self._resize_state.bottom:
            rect.setBottom(rect.bottom() + delta.y())

        rect = rect.normalized()
        if rect.width() < self.minimumWidth() or rect.height() < self.minimumHeight():
            return
        self.setGeometry(rect)

    def _update_resize_cursor(self, point: QPoint) -> None:
        state = self._hit_test_resize(point)
        if (state.left and state.top) or (state.right and state.bottom):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif (state.right and state.top) or (state.left and state.bottom):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif state.left or state.right:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif state.top or state.bottom:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.unsetCursor()


class ManagedWindow(BaseWindow):
    """Concrete managed window that hosts an app widget."""

    def __init__(
        self,
        window_id: str,
        title: str,
        content: QWidget,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(window_id=window_id, title=title, parent=parent)
        self.set_content(content)
