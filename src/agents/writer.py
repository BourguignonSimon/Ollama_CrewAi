"""Writer agent for generating documentation."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from .base import Agent
from .message import Message


@dataclass
class WriterAgent(Agent):
    """Agent that writes documentation files to the filesystem."""

    capabilities: list[str] = field(default_factory=lambda: ["documentation"])
    tools: list[str] = field(default_factory=lambda: ["filesystem"])
    documents: List[Path] = field(default_factory=list)

    def plan(self) -> Message:  # type: ignore[override]
        return Message(sender="writer", content="ready")

    def act(self, message: Message) -> Message:  # type: ignore[override]
        metadata = message.metadata or {}
        path_value = metadata.get("path")
        text = metadata.get("text", "")
        if path_value:
            path = Path(path_value)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            self.documents.append(path)
            return Message(sender="writer", content=f"wrote {path}")
        return Message(sender="writer", content="no document")

    def observe(self, message: Message) -> None:  # type: ignore[override]
        if message.content.startswith("wrote"):
            self.documents.append(Path(message.content.split(" ", 1)[1]))
