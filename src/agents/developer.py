"""Developer agent responsible for code generation and file interactions."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import asyncio

from core.bus import MessageBus

from .base import Agent
from .message import Message


@dataclass
class DeveloperAgent(Agent):
    """Agent that writes provided code snippets to the filesystem."""

    capabilities: list[str] = field(default_factory=lambda: ["coding", "file-writing"])
    tools: list[str] = field(default_factory=lambda: ["filesystem"])
    last_written: Path | None = None
    bus: MessageBus | None = None
    queue: asyncio.Queue[Message] | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        if self.bus:
            self.queue = self.bus.register("developer")

    def plan(self) -> Message:
        return Message(sender="developer", content="ready")

    def act(self, message: Message) -> Message:
        metadata = message.metadata or {}
        path_value = metadata.get("path")
        code = metadata.get("code", "")
        if path_value:
            path = Path(path_value)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(code)
            self.last_written = path
            return Message(sender="developer", content=f"wrote {path}")
        return Message(sender="developer", content="no action")

    def observe(self, message: Message) -> None:
        if message.content.startswith("wrote"):
            self.last_written = Path(message.content.split(" ", 1)[1])
