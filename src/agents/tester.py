"""Tester agent for executing test suites."""
from __future__ import annotations

from dataclasses import dataclass, field
import subprocess
import asyncio
import logging

from core.bus import MessageBus
from core.logging import get_logger

from .base import Agent
from .message import Message


@dataclass
class TesterAgent(Agent):
    """Agent that runs pytest and returns the results."""
    model: str = "gpt-4"
    capabilities: list[str] = field(default_factory=lambda: ["testing"])
    tools: list[str] = field(default_factory=lambda: ["pytest"])
    last_result: str | None = None
    bus: MessageBus | None = None
    queue: asyncio.Queue[Message] | None = field(init=False, default=None)
    logger: logging.LoggerAdapter = field(default_factory=lambda: get_logger("tester"))

    def __post_init__(self) -> None:
        super().__init__(self.logger)
        if self.bus:
            self.queue = self.bus.register("tester")

    def plan(self) -> Message:
        return Message(sender="tester", content="ready")

    async def act(self, message: Message) -> Message:
        command = message.content or "pytest"
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                command.split(),
                capture_output=True,
                text=True,
                check=True,
            )
            self.last_result = result.stdout
            return Message(sender="tester", content="success", metadata={"output": result.stdout})
        except subprocess.CalledProcessError as exc:  # pragma: no cover - failure path
            self.last_result = exc.stderr
            return Message(sender="tester", content="failure", metadata={"error": exc.stderr})

    def observe(self, message: Message) -> None:
        if message.metadata:
            self.last_result = message.metadata.get("output") or message.metadata.get("error")
