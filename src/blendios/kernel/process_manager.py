"""Process manager for the BlendiOS kernel simulation."""

from __future__ import annotations

import threading
from typing import Any

from blendios.constants import DEFAULT_ROUND_ROBIN_QUANTUM_MS, DEFAULT_SCHEDULER
from blendios.exceptions import ProcessError
from blendios.kernel.models import Process, ProcessStatus
from blendios.kernel.scheduler import (
    BaseScheduler,
    FIFOScheduler,
    PriorityScheduler,
    RoundRobinScheduler,
    ShortestJobFirstScheduler,
)


class ProcessManager:
    """Manages the simulated process lifecycle."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._processes: dict[int, Process] = {}
        self._next_pid = 1
        self._scheduler = self._create_scheduler(DEFAULT_SCHEDULER)
        self._quantum_ms = DEFAULT_ROUND_ROBIN_QUANTUM_MS

    @staticmethod
    def _create_scheduler(name: str) -> BaseScheduler:
        schedulers: dict[str, BaseScheduler] = {
            "fifo": FIFOScheduler(),
            "round_robin": RoundRobinScheduler(),
            "priority": PriorityScheduler(),
            "sjf": ShortestJobFirstScheduler(),
        }
        try:
            return schedulers[name.lower()]
        except KeyError as exc:
            raise ProcessError(f"Unknown scheduler: {name}") from exc

    def set_scheduler(self, name: str, quantum_ms: int | None = None) -> None:
        """Switch the active scheduling algorithm."""
        with self._lock:
            self._scheduler = self._create_scheduler(name)
            if quantum_ms is not None:
                self._quantum_ms = quantum_ms

    def create_process(
        self,
        app_id: str,
        user_id: int,
        priority: int = 5,
        memory_mb: int = 0,
        burst_time_ms: int = 1000,
        metadata: dict[str, Any] | None = None,
    ) -> Process:
        """Create and register a new process."""
        with self._lock:
            pid = self._next_pid
            self._next_pid += 1
            process = Process(
                pid=pid,
                app_id=app_id,
                user_id=user_id,
                priority=priority,
                memory_mb=memory_mb,
                burst_time_ms=burst_time_ms,
                remaining_time_ms=burst_time_ms,
                metadata=metadata or {},
            )
            self._processes[pid] = process
            self._scheduler.enqueue(process)
            return process

    def get_process(self, pid: int) -> Process:
        """Return a process by PID."""
        with self._lock:
            if pid not in self._processes:
                raise ProcessError(f"Process {pid} not found")
            return self._processes[pid]

    def list_processes(self, active_only: bool = False) -> list[Process]:
        """Return all or only active processes."""
        with self._lock:
            processes = list(self._processes.values())
            if active_only:
                processes = [p for p in processes if p.is_active()]
            return processes

    def terminate_process(self, pid: int, exit_code: int = 0) -> Process:
        """Terminate a process by PID."""
        with self._lock:
            process = self.get_process(pid)
            process.terminate(exit_code)
            return process

    def tick(self) -> Process | None:
        """Advance the scheduler by one quantum."""
        with self._lock:
            return self._scheduler.tick(self._quantum_ms)

    def scheduler_metrics(self) -> Any:
        """Return current scheduler metrics."""
        with self._lock:
            return self._scheduler.metrics()
