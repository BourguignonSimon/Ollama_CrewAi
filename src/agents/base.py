"""Base agent definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio

from core.bus import MessageBus
from .message import Message


class Agent(ABC):
    """Abstract base class for agents participating in a conversation.

    Subclasses must provide concrete implementations for the planning,
    acting and observing steps of an agent. All communication between
    agents is performed via :class:`~agents.message.Message` instances.
    """

    # Bus integration -------------------------------------------------
    bus: MessageBus | None = None
    queue: asyncio.Queue[Message] | None = None

    @abstractmethod
    def plan(self) -> Message:
        """Generate a plan represented as a :class:`Message`."""

    @abstractmethod
    def act(self, message: Message) -> Message:
        """Perform an action based on ``message`` and return the response.

        Parameters
        ----------
        message:
            The incoming :class:`Message` that should trigger the action.
        """

    @abstractmethod
    def observe(self, message: Message) -> None:
        """Observe an incoming :class:`Message` and update internal state."""

    async def handle(self) -> None:
        """Continuously process incoming messages from the bus.

        Subclasses typically don't override this method; instead they
        implement :meth:`act` and :meth:`observe` while ``handle`` manages
        the bus communication loop.
        """

        if not self.bus or not self.queue:
            raise RuntimeError("Agent is not connected to a message bus")

        while True:
            message = await self.queue.get()
            response = self.act(message)
            self.observe(response)

            metadata: dict[str, object] = {}
            if message.metadata:
                metadata.update(message.metadata)
            if response.metadata:
                metadata.update(response.metadata)
            if metadata:
                response.metadata = metadata

            await self.bus.send("manager", response)
            self.queue.task_done()
