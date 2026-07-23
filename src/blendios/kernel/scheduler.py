"""Pluggable process scheduler implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blendios.kernel.models import Process


@dataclass
class ScheduleMetrics:
    """Metrics reported by a scheduler."""

    algorithm: str
    average_waiting_time: float = 0.0
    average_turnaround_time: float = 0.0
    cpu_utilization: float = 0.0
    throughput: float = 0.0
    context_switches: int = 0


class BaseScheduler(ABC):
    """Abstract base class for process schedulers."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._ready_queue: deque[Process] = deque()
        self._context_switches = 0

    @abstractmethod
    def enqueue(self, process: Process) -> None:
        """Add a process to the ready queue."""

    @abstractmethod
    def tick(self, time_quantum_ms: int) -> Process | None:
        """Advance the scheduler by one time slice and return the active process."""

    def metrics(self) -> ScheduleMetrics:
        """Return current scheduler metrics."""
        return ScheduleMetrics(algorithm=self.name, context_switches=self._context_switches)


class FIFOScheduler(BaseScheduler):
    """First-In-First-Out (non-preemptive) scheduler."""

    def __init__(self) -> None:
        super().__init__("FIFO")

    def enqueue(self, process: Process) -> None:
        self._ready_queue.append(process)

    def tick(self, time_quantum_ms: int) -> Process | None:
        if not self._ready_queue:
            return None
        active = self._ready_queue[0]
        active.burst_time_ms -= time_quantum_ms
        if active.burst_time_ms <= 0:
            self._ready_queue.popleft()
            self._context_switches += 1
        return active


class RoundRobinScheduler(BaseScheduler):
    """Round-robin preemptive scheduler with a fixed time quantum."""

    def __init__(self, quantum_ms: int = 100) -> None:
        super().__init__("Round Robin")
        self.quantum_ms = quantum_ms

    def enqueue(self, process: Process) -> None:
        self._ready_queue.append(process)

    def tick(self, time_quantum_ms: int) -> Process | None:
        if not self._ready_queue:
            return None
        active = self._ready_queue.popleft()
        active.remaining_time_ms -= min(time_quantum_ms, active.remaining_time_ms)
        if active.remaining_time_ms > 0:
            self._ready_queue.append(active)
        self._context_switches += 1
        return active


class PriorityScheduler(BaseScheduler):
    """Priority-based scheduler (lower number = higher priority)."""

    def __init__(self, preemptive: bool = False) -> None:
        super().__init__("Priority")
        self.preemptive = preemptive

    def enqueue(self, process: Process) -> None:
        self._ready_queue.append(process)
        # Keep queue sorted by priority
        self._ready_queue = deque(sorted(self._ready_queue, key=lambda p: p.priority))

    def tick(self, time_quantum_ms: int) -> Process | None:
        if not self._ready_queue:
            return None
        active = self._ready_queue.popleft()
        active.remaining_time_ms -= min(time_quantum_ms, active.remaining_time_ms)
        if active.remaining_time_ms > 0:
            self._ready_queue.appendleft(active) if self.preemptive else self._ready_queue.append(
                active
            )
            self._ready_queue = deque(sorted(self._ready_queue, key=lambda p: p.priority))
        self._context_switches += 1
        return active


class ShortestJobFirstScheduler(BaseScheduler):
    """Non-preemptive shortest-job-first scheduler."""

    def __init__(self) -> None:
        super().__init__("Shortest Job First")

    def enqueue(self, process: Process) -> None:
        self._ready_queue.append(process)
        self._ready_queue = deque(sorted(self._ready_queue, key=lambda p: p.burst_time_ms))

    def tick(self, time_quantum_ms: int) -> Process | None:
        if not self._ready_queue:
            return None
        active = self._ready_queue[0]
        active.remaining_time_ms -= min(time_quantum_ms, active.remaining_time_ms)
        if active.remaining_time_ms <= 0:
            self._ready_queue.popleft()
            self._context_switches += 1
        return active
