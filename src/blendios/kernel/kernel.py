"""Kernel facade for BlendiOS."""

from __future__ import annotations

import logging
from typing import Any

from blendios.kernel.event_bus import EventBus
from blendios.kernel.memory_manager import MemoryManager
from blendios.kernel.process_manager import ProcessManager
from blendios.kernel.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class Kernel:
    """Central kernel facade that coordinates all BlendiOS subsystems."""

    _instance: Kernel | None = None

    def __new__(cls) -> Kernel:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.process_manager = ProcessManager()
        self.memory_manager = MemoryManager()
        self.service_manager = ServiceManager()
        self.event_bus = EventBus()
        self._app_registry: Any | None = None
        self._initialized = True

    def bootstrap(self) -> None:
        """Initialize the kernel and start background services."""
        logger.info("BlendiOS kernel bootstrapping...")
        self.service_manager.start_all()
        logger.info("BlendiOS kernel ready.")

    def shutdown(self) -> None:
        """Gracefully shut down the kernel."""
        logger.info("BlendiOS kernel shutting down...")
        self.service_manager.stop_all()
        for process in self.process_manager.list_processes(active_only=True):
            self.process_manager.terminate_process(process.pid)
        logger.info("BlendiOS kernel stopped.")

    def launch_app(self, app_id: str, user_id: int = 1) -> Any:
        """Launch an application by ID."""
        from blendios.apps.app_registry import AppRegistry

        registry = AppRegistry()
        app_class = registry.get_app_class(app_id)
        if app_class is None:
            raise RuntimeError(f"Unknown app: {app_id}")

        process = self.process_manager.create_process(
            app_id=app_id,
            user_id=user_id,
            memory_mb=64,
        )

        context = registry.create_context(app_id, process.pid, user_id, self)
        app = app_class(context)
        app.on_launch()
        return app
