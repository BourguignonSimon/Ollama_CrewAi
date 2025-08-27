"""Writer agent for generating documentation."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict
import asyncio
import logging

from core.bus import MessageBus
from core.logging import get_logger

from .base import Agent
from .message import Message


@dataclass
class WriterAgent(Agent):
    """Agent that writes documentation files to the filesystem."""
    model: str = "gpt-4"
    capabilities: list[str] = field(default_factory=lambda: ["documentation"])
    tools: list[str] = field(default_factory=lambda: ["filesystem"])
    documents: Dict[Path, str] = field(default_factory=dict)
    bus: MessageBus | None = None
    queue: asyncio.Queue[Message] | None = field(init=False, default=None)
    logger: logging.LoggerAdapter = field(default_factory=lambda: get_logger("writer"))

    def __post_init__(self) -> None:
        super().__init__(self.logger)
        if self.bus:
            self.queue = self.bus.register("writer")

    def plan(self) -> Message:
        return Message(sender="writer", content="ready")

    def act(self, message: Message) -> Message:
        metadata = message.metadata or {}
        path_value = metadata.get("path")
        text = metadata.get("text", "")
        if path_value:
            path = Path(path_value)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            self.documents[path] = text
            return Message(sender="writer", content=f"wrote {path}")
        return Message(sender="writer", content="no document")

    def observe(self, message: Message) -> None:
        if message.content.startswith("wrote"):
            path = Path(message.content.split(" ", 1)[1])
            try:
                self.documents[path] = path.read_text()
            except FileNotFoundError:  # pragma: no cover - file missing
                self.documents[path] = ""
