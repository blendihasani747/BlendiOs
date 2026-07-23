"""Start menu popup for the BlendiOS desktop shell."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QEasingCurve, QPoint, Property, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from blendios.desktop.icon_provider import get_app_icon


class StartMenu(QFrame):
    """Animated start menu with search, pinned apps, and power controls."""

    launch_requested = Signal(str)
    shutdown_requested = Signal()
    restart_requested = Signal()
    lock_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("startMenu")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setFixedSize(500, 560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        profile = QLabel("BlendiOS User")
        profile.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(profile)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search apps, files, settings...")
        self.search.textChanged.connect(self._filter_apps)
        layout.addWidget(self.search)

        pinned_label = QLabel("Pinned")
        pinned_label.setObjectName("caption")
        layout.addWidget(pinned_label)

        self.pinned_grid_host = QWidget()
        self.pinned_grid = QGridLayout(self.pinned_grid_host)
        self.pinned_grid.setContentsMargins(0, 0, 0, 0)
        self.pinned_grid.setSpacing(8)
        layout.addWidget(self.pinned_grid_host)

        all_apps_label = QLabel("All Apps")
        all_apps_label.setObjectName("caption")
        layout.addWidget(all_apps_label)

        self.app_list = QListWidget()
        self.app_list.itemDoubleClicked.connect(self._launch_item)
        layout.addWidget(self.app_list, 1)

        recent_label = QLabel("Recent Files")
        recent_label.setObjectName("caption")
        layout.addWidget(recent_label)

        self.recent_files = QListWidget()
        self.recent_files.setMaximumHeight(90)
        self.recent_files.addItem("No recent files")
        layout.addWidget(self.recent_files)

        footer = QHBoxLayout()
        lock_button = QPushButton("Lock")
        lock_button.clicked.connect(self.lock_requested.emit)
        restart_button = QPushButton("Restart")
        restart_button.clicked.connect(self.restart_requested.emit)
        shutdown_button = QPushButton("Shutdown")
        shutdown_button.clicked.connect(self.shutdown_requested.emit)
        footer.addWidget(lock_button)
        footer.addWidget(restart_button)
        footer.addWidget(shutdown_button)
        layout.addLayout(footer)

        self._app_metadata: list[dict] = []
        self._offset = QPoint(0, 0)

    def get_offset(self) -> QPoint:
        return self._offset

    def set_offset(self, value: QPoint) -> None:
        self._offset = value
        self.move(self.pos() + value)

    offset = Property(QPoint, get_offset, set_offset)

    def set_apps(self, apps: list[dict], pinned_limit: int = 6) -> None:
        self._app_metadata = sorted(apps, key=lambda item: item["name"].lower())
        self._render_pinned(self._app_metadata[:pinned_limit])
        self._render_list(self._app_metadata)

    def show_animated(self, pos: QPoint) -> None:
        self.move(pos.x(), pos.y() + 20)
        self.show()
        self.raise_()

        animation = QPropertyAnimation(self, b"pos", self)
        animation.setDuration(220)
        animation.setStartValue(QPoint(pos.x(), pos.y() + 20))
        animation.setEndValue(pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()

    def _render_pinned(self, apps: list[dict]) -> None:
        while self.pinned_grid.count():
            item = self.pinned_grid.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        for index, app in enumerate(apps):
            button = QPushButton(app["name"])
            button.setFixedHeight(36)
            button.setIcon(get_app_icon(self.style(), app["app_id"]))
            button.clicked.connect(self._make_launch_handler(app["app_id"]))
            row = index // 3
            col = index % 3
            self.pinned_grid.addWidget(button, row, col)

    def _render_list(self, apps: list[dict]) -> None:
        self.app_list.clear()
        for app in apps:
            item = QListWidgetItem(app["name"])
            item.setIcon(get_app_icon(self.style(), app["app_id"]))
            item.setData(Qt.ItemDataRole.UserRole, app["app_id"])
            self.app_list.addItem(item)

    def _make_launch_handler(self, app_id: str) -> Callable[[], None]:
        return lambda: self.launch_requested.emit(app_id)

    def _launch_item(self, item: QListWidgetItem) -> None:
        app_id = item.data(Qt.ItemDataRole.UserRole)
        if app_id:
            self.launch_requested.emit(app_id)

    def _filter_apps(self, text: str) -> None:
        query = text.strip().lower()
        if not query:
            self._render_list(self._app_metadata)
            return

        filtered = [
            app
            for app in self._app_metadata
            if query in app["name"].lower() or query in app["app_id"].lower()
        ]
        self._render_list(filtered)
