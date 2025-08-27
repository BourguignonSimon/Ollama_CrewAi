"""Researcher agent for web information gathering."""
from __future__ import annotations

from dataclasses import dataclass, field
import asyncio
import aiohttp
import logging

from core.bus import MessageBus
from core.logging import get_logger

from .base import Agent
from .message import Message


@dataclass
class ResearcherAgent(Agent):
    """Agent that fetches information from the web using ``aiohttp``.

    The :meth:`act` method performs an asynchronous HTTP GET request and
    returns the first 200 characters of the response body.
    """
    model: str = "mistral"
    capabilities: list[str] = field(default_factory=lambda: ["research", "web-fetch"])
    tools: list[str] = field(default_factory=lambda: ["aiohttp"])
    last_response: str | None = None
    bus: MessageBus | None = None
    queue: asyncio.Queue[Message] | None = field(init=False, default=None)
    logger: logging.LoggerAdapter = field(default_factory=lambda: get_logger("researcher"))

    def __post_init__(self) -> None:
        super().__init__(self.logger)
        if self.bus:
            self.queue = self.bus.register("researcher")

    def plan(self) -> Message:
        return Message(sender="researcher", content="ready")

    async def act(self, message: Message) -> Message:
        url = message.content
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    text = await response.text()
            text = text[:200]
            self.last_response = text
            return Message(sender="researcher", content=text)
        except Exception as exc:  # pragma: no cover - network error paths
            error = f"error: {exc}"
            self.last_response = error
            return Message(sender="researcher", content=error)

    def observe(self, message: Message) -> None:
        self.last_response = message.content
