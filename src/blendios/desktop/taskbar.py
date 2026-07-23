"""Taskbar widget for the BlendiOS desktop shell."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QSize, QTimer, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QStyle, QToolButton, QVBoxLayout, QWidget

from blendios.desktop.icon_provider import get_app_icon


class TaskbarAppButton(QWidget):
    """Taskbar app icon with running indicator."""

    clicked = Signal(str)

    def __init__(self, app_id: str, label: str) -> None:
        super().__init__()
        self.app_id = app_id
        self._active = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.button = QToolButton()
        self.button.setFixedSize(38, 30)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.setToolTip(label)
        self.button.setIcon(get_app_icon(self.style(), app_id))
        self.button.setIconSize(QSize(20, 20))
        self.button.clicked.connect(lambda: self.clicked.emit(self.app_id))
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.indicator = QLabel("•")
        self.indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.indicator.setFixedHeight(8)
        self.indicator.setStyleSheet("color: transparent;")
        layout.addWidget(self.indicator)

    def set_active(self, active: bool) -> None:
        self._active = active
        if active:
            self.indicator.setStyleSheet("color: #4cc9f0; font-size: 14px;")
        else:
            self.indicator.setStyleSheet("color: transparent;")


class Taskbar(QWidget):
    """Taskbar with launcher area, active title, and system tray controls."""

    start_requested = Signal()
    notifications_requested = Signal()
    quick_settings_requested = Signal()
    app_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("taskbar")
        self.setFixedHeight(60)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 8, 10, 8)
        self.layout.setSpacing(8)

        self.start_button = QPushButton("Blend")
        self.start_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMenuButton))
        self.start_button.setFixedHeight(40)
        self.start_button.clicked.connect(self.start_requested.emit)
        self.layout.addWidget(self.start_button)

        self.apps_row = QHBoxLayout()
        self.apps_row.setSpacing(4)
        self.layout.addLayout(self.apps_row)

        self.layout.addSpacing(16)

        self.active_window_label = QLabel("Desktop")
        self.active_window_label.setObjectName("caption")
        self.layout.addWidget(self.active_window_label)
        self.layout.addStretch(1)

        self.quick_settings_button = QPushButton("Panel")
        self.quick_settings_button.setFixedSize(62, 34)
        self.quick_settings_button.clicked.connect(self.quick_settings_requested.emit)
        self.layout.addWidget(self.quick_settings_button)

        self.notification_button = QPushButton("Alerts")
        self.notification_button.setFixedSize(64, 34)
        self.notification_button.clicked.connect(self.notifications_requested.emit)
        self.layout.addWidget(self.notification_button)

        self.clock_label = QLabel("00:00")
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock_label.setFixedWidth(72)
        self.layout.addWidget(self.clock_label)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_clock)
        self._timer.start(1000)
        self._update_clock()

        self._app_buttons: dict[str, TaskbarAppButton] = {}

    def _update_clock(self) -> None:
        now = datetime.now()
        self.clock_label.setText(now.strftime("%H:%M"))

    def register_app(self, app_id: str, label: str) -> None:
        if app_id in self._app_buttons:
            return
        button = TaskbarAppButton(app_id, label)
        button.clicked.connect(self.app_requested.emit)
        self.apps_row.addWidget(button)
        self._app_buttons[app_id] = button

    def set_running(self, app_id: str, running: bool) -> None:
        button = self._app_buttons.get(app_id)
        if button:
            button.set_active(running)

    def set_active_window_title(self, title: str) -> None:
        self.active_window_label.setText(title or "Desktop")
