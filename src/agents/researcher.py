"""Researcher agent for web information gathering."""
from __future__ import annotations

from dataclasses import dataclass, field
import requests
import asyncio

from core.bus import MessageBus

from .base import Agent
from .message import Message


@dataclass
class ResearcherAgent(Agent):
    """Agent that fetches information from the web using ``requests``."""

    capabilities: list[str] = field(default_factory=lambda: ["research", "web-fetch"])
    tools: list[str] = field(default_factory=lambda: ["requests"])
    last_response: str | None = None
    bus: MessageBus | None = None
    queue: asyncio.Queue[Message] | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        if self.bus:
            self.queue = self.bus.register("researcher")

    def plan(self) -> Message:  # type: ignore[override]
        return Message(sender="researcher", content="ready")

    def act(self, message: Message) -> Message:  # type: ignore[override]
        url = message.content
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            text = response.text[:200]
            self.last_response = text
            return Message(sender="researcher", content=text)
        except Exception as exc:  # pragma: no cover - network error paths
            error = f"error: {exc}"
            self.last_response = error
            return Message(sender="researcher", content=error)

    def observe(self, message: Message) -> None:  # type: ignore[override]
        self.last_response = message.content
