import pathlib
import sys

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents.manager import Manager
from core import MessageBus, TaskStatus


class EchoAgent(Agent):
    """Agent that echoes back the uppercase content of messages."""

    def __init__(self, name: str, bus: MessageBus) -> None:
        self.name = name
        self.bus = bus
        self.queue = bus.register(name)

    def plan(self) -> Message:  # type: ignore[override]
        return Message(sender=self.name, content="ready")

    def act(self, message: Message) -> Message:  # type: ignore[override]
        return Message(sender=self.name, content=message.content.upper(), metadata=message.metadata)

    def observe(self, message: Message) -> None:  # type: ignore[override]
        pass


@pytest.mark.asyncio
async def test_complete_task_flow() -> None:
    bus = MessageBus()
    echo = EchoAgent("worker", bus)
    manager = Manager({"worker": echo}, bus=bus)

    tasks = await manager.run("alpha. beta.")

    assert [t.result for t in tasks] == ["ALPHA", "BETA"]
    assert all(t.status is TaskStatus.DONE for t in tasks)
