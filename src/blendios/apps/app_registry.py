"""Application registry for BlendiOS."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from blendios.apps.base_app import AppContext

if TYPE_CHECKING:
    from blendios.kernel.kernel import Kernel


class AppRegistry:
    """Registry of all internal and plugin-provided applications."""

    _instance: AppRegistry | None = None
    _apps: dict[str, type] = {}

    def __new__(cls) -> AppRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._register_builtin_apps()

    def _register_builtin_apps(self) -> None:
        """Lazy-register built-in apps to avoid circular imports."""
        if self._apps:
            return

        from blendios.apps.browser.browser_app import BrowserApp
        from blendios.apps.calculator.calculator_app import CalculatorApp
        from blendios.apps.file_explorer.file_explorer_app import FileExplorerApp
        from blendios.apps.notes.notes_app import NotesApp
        from blendios.apps.settings.settings_app import SettingsApp
        from blendios.apps.terminal.terminal_app import TerminalApp

        self._apps = {
            BrowserApp.app_id: BrowserApp,
            FileExplorerApp.app_id: FileExplorerApp,
            TerminalApp.app_id: TerminalApp,
            CalculatorApp.app_id: CalculatorApp,
            NotesApp.app_id: NotesApp,
            SettingsApp.app_id: SettingsApp,
        }

    def register(self, app_id: str, app_class: type) -> None:
        """Register an application class."""
        self._apps[app_id] = app_class

    def get_app_class(self, app_id: str) -> type | None:
        """Return the application class for the given ID."""
        return self._apps.get(app_id)

    def list_apps(self) -> list[dict[str, Any]]:
        """Return metadata for all registered apps."""
        return [
            {
                "app_id": app_class.app_id,
                "name": app_class.name,
                "version": app_class.version,
                "icon": app_class.icon,
                "category": app_class.category,
            }
            for app_class in self._apps.values()
        ]

    def create_context(
        self, app_id: str, process_id: int, user_id: int, kernel: Kernel
    ) -> AppContext:
        """Create an AppContext for a launching app."""
        return AppContext(
            app_id=app_id,
            user_id=user_id,
            process_id=process_id,
            kernel=kernel,
            vfs=None,  # TODO: wire VFS
            api_client=None,  # TODO: wire API client
            settings={},
        )
