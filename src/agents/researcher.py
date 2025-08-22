"""Researcher agent for web information gathering."""
from __future__ import annotations

from dataclasses import dataclass, field
import requests

from .base import Agent
from .message import Message


@dataclass
class ResearcherAgent(Agent):
    """Agent that fetches information from the web using ``requests``."""

    capabilities: list[str] = field(default_factory=lambda: ["research", "web-fetch"])
    tools: list[str] = field(default_factory=lambda: ["requests"])
    last_response: str | None = None

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
