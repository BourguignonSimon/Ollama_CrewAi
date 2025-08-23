from __future__ import annotations

import asyncio
from typing import Dict

from agents.message import Message


class MessageBus:
    """Simple asynchronous message bus based on ``asyncio`` queues."""

    def __init__(self) -> None:
        self._queues: Dict[str, asyncio.Queue[Message]] = {}
        # Pre-register supervisor channel for UI communications
        self.register("supervisor")

    def register(self, name: str) -> asyncio.Queue[Message]:
        """Register ``name`` and return its message queue."""
        queue: asyncio.Queue[Message] = asyncio.Queue()
        self._queues[name] = queue
        return queue

    async def send(self, target: str, message: Message) -> None:
        """Send ``message`` to ``target``'s queue."""
        queue = self._queues.get(target)
        if queue is None:
            raise KeyError(f"No queue registered for {target}")
        await queue.put(message)

    def dispatch(self, target: str, message: Message) -> None:
        """Synchronously send ``message`` to ``target`` if possible."""
        queue = self._queues.get(target)
        if queue is None:
            raise KeyError(f"No queue registered for {target}")
        queue.put_nowait(message)

    # -- Supervisor convenience API -----------------------------------
    def send_to_supervisor(self, message: Message) -> None:
        """Synchronously send ``message`` to the supervisor queue."""
        self.dispatch("supervisor", message)

    async def recv_from_supervisor(self) -> Message:
        """Receive the next message from the supervisor queue."""
        queue = self._queues.get("supervisor")
        if queue is None:
            raise KeyError("No queue registered for supervisor")
        return await queue.get()
