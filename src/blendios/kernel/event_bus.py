"""Async publish/subscribe event bus for BlendiOS."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine


class EventBus:
    """In-memory async event bus."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[Any], Coroutine[Any, Any, None]]]] = defaultdict(
            list
        )
        self._lock = asyncio.Lock()

    async def subscribe(
        self, event_type: str, handler: Callable[[Any], Coroutine[Any, Any, None]]
    ) -> None:
        """Subscribe a coroutine handler to an event type."""
        async with self._lock:
            self._subscribers[event_type].append(handler)

    async def publish(self, event_type: str, payload: Any) -> None:
        """Publish an event to all subscribers."""
        handlers = []
        async with self._lock:
            handlers = list(self._subscribers.get(event_type, []))
        await asyncio.gather(*(handler(payload) for handler in handlers), return_exceptions=True)

    async def unsubscribe(
        self, event_type: str, handler: Callable[[Any], Coroutine[Any, Any, None]]
    ) -> None:
        """Remove a handler from an event type."""
        async with self._lock:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
