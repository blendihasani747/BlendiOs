"""Base application class for BlendiOS internal apps."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


@dataclass
class AppContext:
    """Context passed to every app on launch."""

    app_id: str
    user_id: int
    process_id: int
    kernel: Any  # Kernel facade
    vfs: Any  # VirtualFileSystem
    api_client: Any  # API client
    settings: dict[str, Any]

    def shutdown(self) -> None:
        """Request the kernel to terminate this app."""
        self.kernel.process_manager.terminate_process(self.process_id)


class BaseApp(ABC):
    """Abstract base class for all BlendiOS applications."""

    app_id: str = "base_app"
    name: str = "Base App"
    version: str = "0.1.0"
    icon: str = "icons/default_app.png"
    category: str = "utilities"
    required_permissions: tuple[str, ...] = ()

    def __init__(self, context: AppContext) -> None:
        self.context = context
        self._main_window: QWidget | None = None

    @abstractmethod
    def build_ui(self) -> QWidget:
        """Build and return the app's main PySide6 widget."""

    @abstractmethod
    def on_launch(self) -> None:
        """Called once when the app is launched."""

    def on_close(self) -> None:
        """Called when the app window is closed. Override for cleanup."""
        self.context.shutdown()

    def get_main_window(self) -> QWidget:
        """Lazy-create and return the main window."""
        if self._main_window is None:
            self._main_window = self.build_ui()
        return self._main_window
