"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from blendios.kernel.memory_manager import MemoryManager
from blendios.kernel.process_manager import ProcessManager
from blendios.kernel.scheduler import RoundRobinScheduler


@pytest.fixture
def process_manager() -> ProcessManager:
    """Return a fresh process manager for tests."""
    return ProcessManager()


@pytest.fixture
def memory_manager() -> MemoryManager:
    """Return a fresh memory manager for tests."""
    return MemoryManager(total_mb=1024)


@pytest.fixture
def round_robin_scheduler() -> RoundRobinScheduler:
    """Return a round-robin scheduler for tests."""
    return RoundRobinScheduler(quantum_ms=100)
