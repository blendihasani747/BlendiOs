"""Kernel domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from blendios.constants import (
    PROCESS_CRASHED,
    PROCESS_RUNNING,
    PROCESS_SLEEPING,
    PROCESS_STOPPED,
    PROCESS_TERMINATED,
)


class ProcessStatus(str, Enum):
    """Process lifecycle statuses."""

    RUNNING = PROCESS_RUNNING
    SLEEPING = PROCESS_SLEEPING
    STOPPED = PROCESS_STOPPED
    TERMINATED = PROCESS_TERMINATED
    CRASHED = PROCESS_CRASHED


@dataclass
class Process:
    """Represents a simulated OS process."""

    pid: int
    app_id: str
    user_id: int
    status: ProcessStatus = ProcessStatus.RUNNING
    priority: int = 5
    memory_mb: int = 0
    cpu_percent: float = 0.0
    burst_time_ms: int = 0
    remaining_time_ms: int = 0
    arrival_time: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None
    exit_code: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_active(self) -> bool:
        """Return True if the process has not finished."""
        return self.status not in (
            ProcessStatus.TERMINATED,
            ProcessStatus.CRASHED,
        )

    def terminate(self, exit_code: int = 0) -> None:
        """Mark the process as terminated."""
        self.status = ProcessStatus.TERMINATED
        self.exit_code = exit_code
        self.ended_at = datetime.utcnow()


@dataclass
class Service:
    """Represents a long-running background service."""

    service_id: str
    name: str
    entry_point: str
    auto_start: bool = True
    restart_on_crash: bool = True
    is_running: bool = False
    pid: int | None = None


@dataclass
class SystemStats:
    """Snapshot of simulated system statistics."""

    uptime_seconds: float
    cpu_percent: float
    memory_total_mb: int
    memory_used_mb: int
    memory_free_mb: int
    process_count: int
    active_user_count: int
