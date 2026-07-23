"""Notification center and toast notifications for BlendiOS."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime

from PySide6.QtCore import QEasingCurve, QPoint, Property, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


@dataclass(slots=True)
class NotificationItem:
    """Immutable notification payload."""

    app_id: str
    title: str
    message: str
    created_at: datetime


class ToastNotification(QFrame):
    """Animated single toast notification."""

    dismissed = Signal()

    def __init__(self, title: str, message: str, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("surface")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(320, 92)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(title_label)

        body_label = QLabel(message)
        body_label.setWordWrap(True)
        body_label.setObjectName("caption")
        layout.addWidget(body_label)

        self._offset = QPoint(0, 0)

    def get_offset(self) -> QPoint:
        return self._offset

    def set_offset(self, value: QPoint) -> None:
        self._offset = value
        self.move(self.pos() + value)

    offset = Property(QPoint, get_offset, set_offset)

    def show_animated(self, x: int, y: int, duration_ms: int = 220) -> None:
        self.move(x, y + 24)
        self.show()

        animation = QPropertyAnimation(self, b"pos", self)
        animation.setDuration(duration_ms)
        animation.setStartValue(QPoint(x, y + 24))
        animation.setEndValue(QPoint(x, y))
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()

        QTimer.singleShot(3600, self.close)

    def closeEvent(self, event: QCloseEvent) -> None:  # type: ignore[override]
        self.dismissed.emit()
        super().closeEvent(event)


class NotificationCenter(QFrame):
    """Slide-out notification history panel."""

    clear_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("surface")
        self.setFixedWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Notifications")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        header.addWidget(title)
        header.addStretch(1)

        clear_button = QPushButton("Dismiss All")
        clear_button.clicked.connect(self.clear_requested.emit)
        header.addWidget(clear_button)
        layout.addLayout(header)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget, 1)

    def add(self, item: NotificationItem) -> None:
        stamp = item.created_at.strftime("%H:%M")
        row = QListWidgetItem(f"[{stamp}] {item.title}\n{item.message}")
        self.list_widget.insertItem(0, row)

    def clear(self) -> None:
        self.list_widget.clear()


class NotificationManager(QWidget):
    """Coordinator for toast + notification center history."""

    def __init__(self, host: QWidget) -> None:
        super().__init__(host)
        self._host = host
        self._items: deque[NotificationItem] = deque(maxlen=200)
        self._active_toasts: list[ToastNotification] = []
        self.center = NotificationCenter(host)
        self.center.hide()
        self.center.clear_requested.connect(self.clear)

    def push(self, app_id: str, title: str, message: str) -> None:
        item = NotificationItem(
            app_id=app_id,
            title=title,
            message=message,
            created_at=datetime.now(),
        )
        self._items.append(item)
        self.center.add(item)
        self._show_toast(item)

    def toggle_center(self) -> None:
        if self.center.isVisible():
            self.center.hide()
            return
        host_rect = self._host.rect()
        self.center.setGeometry(host_rect.width() - 372, 76, 360, host_rect.height() - 152)
        self.center.show()
        self.center.raise_()

    def clear(self) -> None:
        self._items.clear()
        self.center.clear()

    def _show_toast(self, item: NotificationItem) -> None:
        toast = ToastNotification(item.title, item.message, self._host)
        toast.dismissed.connect(lambda: self._remove_toast(toast))
        self._active_toasts.append(toast)

        host_rect = self._host.rect()
        y_offset = 88 + (len(self._active_toasts) - 1) * 100
        toast.show_animated(host_rect.width() - toast.width() - 20, host_rect.height() - y_offset)

    def _remove_toast(self, toast: ToastNotification) -> None:
        if toast in self._active_toasts:
            self._active_toasts.remove(toast)
