"""Planner agent for project decomposition."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .base import Agent
from .message import Message


@dataclass
class PlannerAgent(Agent):
    """Agent that decomposes objectives into smaller tasks."""

    capabilities: list[str] = field(default_factory=lambda: ["planning", "decomposition"])
    tools: list[str] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)

    def plan(self) -> Message:  # type: ignore[override]
        """Return a simple readiness message."""
        return Message(sender="planner", content="ready")

    def act(self, message: Message) -> Message:  # type: ignore[override]
        """Split the incoming objective into discrete tasks."""
        self.tasks = [t.strip() for t in message.content.split(".") if t.strip()]
        return Message(sender="planner", content="plan", metadata={"tasks": self.tasks})

    def observe(self, message: Message) -> None:  # type: ignore[override]
        """Store observed tasks for later reference."""
        if message.metadata:
            self.tasks = message.metadata.get("tasks", [])
