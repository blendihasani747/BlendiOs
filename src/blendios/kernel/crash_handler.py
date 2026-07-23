"""Crash handling and recovery for BlendiOS."""

from __future__ import annotations

import logging
import traceback
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CrashReport:
    """Details of a system crash or unhandled exception."""

    component: str
    exception: str
    traceback: str
    timestamp: datetime
    context: dict[str, Any]


class CrashHandler:
    """Captures exceptions, logs them, and attempts recovery."""

    def __init__(self) -> None:
        self._history: list[CrashReport] = []

    def handle(
        self,
        exception: BaseException,
        component: str = "unknown",
        context: dict[str, Any] | None = None,
    ) -> CrashReport:
        """Handle an exception and produce a crash report."""
        report = CrashReport(
            component=component,
            exception=type(exception).__name__,
            traceback="".join(traceback.format_exception(exception)),
            timestamp=datetime.utcnow(),
            context=context or {},
        )
        self._history.append(report)
        logger.error(
            "Crash in %s: %s",
            component,
            report.exception,
            extra={"traceback": report.traceback, "context": report.context},
        )
        return report

    def restart_service(self, service_id: str) -> bool:
        """Attempt to restart a failed service."""
        logger.info("Attempting restart of service: %s", service_id)
        # TODO: integrate with ServiceManager
        return False

    def history(self) -> list[CrashReport]:
        """Return crash history."""
        return self._history.copy()
