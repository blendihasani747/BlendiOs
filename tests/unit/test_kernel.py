"""Unit tests for the kernel subsystem."""

from __future__ import annotations

import pytest

from blendios.kernel.models import ProcessStatus
from blendios.kernel.process_manager import ProcessManager
from blendios.kernel.scheduler import RoundRobinScheduler


def test_create_process(process_manager: ProcessManager) -> None:
    process = process_manager.create_process(
        app_id="terminal", user_id=1, priority=3, memory_mb=64, burst_time_ms=500
    )
    assert process.pid == 1
    assert process.app_id == "terminal"
    assert process.status == ProcessStatus.RUNNING


def test_terminate_process(process_manager: ProcessManager) -> None:
    process = process_manager.create_process(app_id="terminal", user_id=1)
    terminated = process_manager.terminate_process(process.pid)
    assert terminated.status == ProcessStatus.TERMINATED
    assert terminated.exit_code == 0


def test_round_robin_scheduler_tick(round_robin_scheduler: RoundRobinScheduler) -> None:
    from blendios.kernel.models import Process

    p = Process(pid=1, app_id="test", user_id=1, remaining_time_ms=250)
    round_robin_scheduler.enqueue(p)
    active = round_robin_scheduler.tick(100)
    assert active is not None
    assert active.remaining_time_ms == 150
