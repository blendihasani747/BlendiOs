"""Simulated memory manager for the BlendiOS kernel."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

from blendios.constants import DEFAULT_TOTAL_RAM_MB
from blendios.exceptions import OutOfMemoryError


@dataclass
class MemoryBlock:
    """A contiguous region of simulated memory."""

    start: int
    size: int
    pid: int | None = None
    is_free: bool = True


@dataclass
class MemoryStats:
    """Snapshot of simulated memory statistics."""

    total_mb: int
    used_mb: int
    free_mb: int
    used_percent: float
    blocks: list[MemoryBlock] = field(default_factory=list)


class MemoryManager:
    """Simulates RAM allocation and deallocation for processes."""

    def __init__(self, total_mb: int = DEFAULT_TOTAL_RAM_MB) -> None:
        self.total_mb = total_mb
        self._lock = threading.RLock()
        # Reserve kernel memory (e.g., 256 MB)
        kernel_mb = 256
        self._blocks: list[MemoryBlock] = [
            MemoryBlock(start=0, size=kernel_mb, pid=0, is_free=False),
            MemoryBlock(start=kernel_mb, size=total_mb - kernel_mb, pid=None, is_free=True),
        ]

    def allocate(self, pid: int, size_mb: int, strategy: str = "first_fit") -> int:
        """Allocate memory for a process and return the starting address."""
        with self._lock:
            candidates = [(i, b) for i, b in enumerate(self._blocks) if b.is_free and b.size >= size_mb]
            if not candidates:
                raise OutOfMemoryError(f"Cannot allocate {size_mb} MB")

            if strategy == "best_fit":
                index, block = min(candidates, key=lambda x: x[1].size)
            elif strategy == "worst_fit":
                index, block = max(candidates, key=lambda x: x[1].size)
            else:  # first_fit
                index, block = candidates[0]

            allocated = MemoryBlock(start=block.start, size=size_mb, pid=pid, is_free=False)
            remaining = block.size - size_mb

            self._blocks[index] = allocated
            if remaining > 0:
                self._blocks.insert(
                    index + 1,
                    MemoryBlock(start=block.start + size_mb, size=remaining, pid=None, is_free=True),
                )
            return allocated.start

    def deallocate(self, pid: int) -> int:
        """Free all memory blocks owned by a process. Returns freed MB."""
        with self._lock:
            freed = 0
            for block in self._blocks:
                if block.pid == pid:
                    block.pid = None
                    block.is_free = True
                    freed += block.size
            self._coalesce()
            return freed

    def _coalesce(self) -> None:
        """Merge adjacent free blocks."""
        merged: list[MemoryBlock] = []
        for block in self._blocks:
            if block.is_free and merged and merged[-1].is_free:
                merged[-1].size += block.size
            else:
                merged.append(block)
        self._blocks = merged

    def stats(self) -> MemoryStats:
        """Return current memory statistics."""
        with self._lock:
            used = sum(b.size for b in self._blocks if not b.is_free)
            free = self.total_mb - used
            used_percent = (used / self.total_mb) * 100 if self.total_mb else 0.0
            return MemoryStats(
                total_mb=self.total_mb,
                used_mb=used,
                free_mb=free,
                used_percent=used_percent,
                blocks=[MemoryBlock(b.start, b.size, b.pid, b.is_free) for b in self._blocks],
            )
