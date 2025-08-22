import pathlib
import sys

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents.manager import Manager


class WorkerAgent(Agent):
    """Simple agent that capitalizes tasks it receives."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.observed: list[Message] = []

    def plan(self) -> Message:  # type: ignore[override]
        return Message(sender=self.name, content="ready")

    def act(self, message: Message) -> Message:  # type: ignore[override]
        self.observed.append(message)
        return Message(sender=self.name, content=message.content.upper())

    def observe(self, message: Message) -> None:  # type: ignore[override]
        self.observed.append(message)


@pytest.mark.asyncio
async def test_manager_orchestration() -> None:
    worker1 = WorkerAgent("w1")
    worker2 = WorkerAgent("w2")
    manager = Manager({"w1": worker1, "w2": worker2})

    results = await manager.run("alpha. beta.")

    assert [msg.content for msg in results] == ["ALPHA", "BETA"]
    assert worker1.observed[0].content == "alpha"
    assert worker2.observed[0].content == "beta"
