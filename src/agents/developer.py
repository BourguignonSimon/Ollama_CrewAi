"""Developer agent responsible for code generation and file interactions."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import asyncio
import logging

from core.bus import MessageBus
from core.logging import get_logger

from .base import Agent
from .message import Message


@dataclass
class DeveloperAgent(Agent):
    """Agent that writes provided code snippets to the filesystem."""
    model: str = "gpt-4"
    capabilities: list[str] = field(
        default_factory=lambda: ["coding", "file-writing", "file-reading"]
    )
    tools: list[str] = field(default_factory=lambda: ["filesystem"])
    last_written: Path | None = None
    bus: MessageBus | None = None
    queue: asyncio.Queue[Message] | None = field(init=False, default=None)
    logger: logging.LoggerAdapter = field(default_factory=lambda: get_logger("developer"))

    def __post_init__(self) -> None:
        super().__init__(self.logger)
        if self.bus:
            self.queue = self.bus.register("developer")

    def plan(self) -> Message:
        return Message(sender="developer", content="ready")

    def act(self, message: Message) -> Message:
        metadata = message.metadata or {}
        path_value = metadata.get("path")
        code = metadata.get("code", "")
        read_path = metadata.get("read")
        if path_value:
            path = Path(path_value)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(code)
            self.last_written = path
            return Message(sender="developer", content=f"wrote {path}")
        if read_path:
            path = Path(read_path)
            try:
                content = path.read_text()
            except FileNotFoundError:
                content = "file not found"
            return Message(sender="developer", content=content)
        return Message(sender="developer", content="no action")

    def observe(self, message: Message) -> None:
        if message.content.startswith("wrote"):
            self.last_written = Path(message.content.split(" ", 1)[1])
