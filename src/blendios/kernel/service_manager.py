"""Background service manager for BlendiOS."""

from __future__ import annotations

import threading
from typing import Any

from blendios.kernel.models import Service


class ServiceManager:
    """Registers and supervises long-running background services."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._services: dict[str, Service] = {}

    def register(self, service: Service) -> None:
        """Register a service definition."""
        with self._lock:
            self._services[service.service_id] = service

    def start_all(self) -> None:
        """Start all services marked for auto-start."""
        with self._lock:
            for service in self._services.values():
                if service.auto_start and not service.is_running:
                    self._start(service)

    def _start(self, service: Service) -> None:
        """Start a single service."""
        service.is_running = True
        # TODO: load entry_point and run in background thread/task

    def stop_all(self) -> None:
        """Stop all running services."""
        with self._lock:
            for service in self._services.values():
                if service.is_running:
                    service.is_running = False

    def list_services(self) -> list[Service]:
        """Return all registered services."""
        with self._lock:
            return list(self._services.values())

    def get_service(self, service_id: str) -> Service | None:
        """Return a service by ID."""
        with self._lock:
            return self._services.get(service_id)
