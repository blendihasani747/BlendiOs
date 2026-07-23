"""Window manager for BlendiOS."""

from __future__ import annotations

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QWidget

from blendios.window_manager.window import ManagedWindow


class WindowManager:
    """Singleton manager for all application windows."""

    _instance: WindowManager | None = None
    _counter = 0

    def __new__(cls) -> WindowManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._windows: dict[str, ManagedWindow] = {}
            cls._instance._z_order: list[str] = []
            cls._instance._on_focus = None
            cls._instance._on_close = None
        return cls._instance

    def set_callbacks(self, on_focus=None, on_close=None) -> None:
        """Set optional callbacks for shell integration."""
        self._on_focus = on_focus
        self._on_close = on_close

    def create_window(
        self,
        title: str,
        content: QWidget,
        parent: QWidget | None = None,
        app_id: str | None = None,
    ) -> ManagedWindow:
        """Create a new managed window."""
        WindowManager._counter += 1
        window_id = f"win_{WindowManager._counter}"

        window = ManagedWindow(
            window_id=window_id,
            title=title,
            content=content,
            parent=parent,
        )
        window.app_id = app_id  # type: ignore[attr-defined]

        # Center on screen if no parent
        if parent is None:
            screen = QApplication.primaryScreen().availableGeometry()
            window.move(
                QPoint(
                    screen.center().x() - window.width() // 2,
                    screen.center().y() - window.height() // 2,
                )
            )

        self._windows[window_id] = window
        self._z_order.append(window_id)
        window.focused.connect(self.focus_window)
        window.closed.connect(self._handle_window_closed)

        window.show()
        window.animate_open()
        window.raise_()
        window.activateWindow()

        if callable(self._on_focus):
            self._on_focus(window)
        return window

    def close_window(self, window_id: str) -> None:
        """Close a managed window."""
        window = self._windows.pop(window_id, None)
        if window:
            window.close()
            if window_id in self._z_order:
                self._z_order.remove(window_id)

    def focus_window(self, window_id: str) -> None:
        """Bring a window to the front."""
        window = self._windows.get(window_id)
        if window:
            window.raise_()
            window.activateWindow()
            if window_id in self._z_order:
                self._z_order.remove(window_id)
            self._z_order.append(window_id)
            if callable(self._on_focus):
                self._on_focus(window)

    def list_windows(self) -> list[ManagedWindow]:
        """Return all managed windows."""
        return list(self._windows.values())

    def _handle_window_closed(self, window_id: str) -> None:
        window = self._windows.pop(window_id, None)
        if window_id in self._z_order:
            self._z_order.remove(window_id)
        if callable(self._on_close):
            self._on_close(window)
