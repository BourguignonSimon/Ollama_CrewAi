"""Base agent definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .message import Message


class Agent(ABC):
    """Abstract base class for agents participating in a conversation.

    Subclasses must provide concrete implementations for the planning,
    acting and observing steps of an agent. All communication between
    agents is performed via :class:`~agents.message.Message` instances.
    """

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
