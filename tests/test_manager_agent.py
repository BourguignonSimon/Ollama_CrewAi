import pathlib
import sys

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents.manager import Manager
from core import MessageBus, TaskStatus


class WorkerAgent(Agent):
    """Simple agent that capitalizes tasks it receives."""

    def __init__(self, name: str, bus: MessageBus) -> None:
        self.name = name
        self.bus = bus
        self.queue = bus.register(name)
        self.observed: list[Message] = []

    def plan(self) -> Message:  # type: ignore[override]
        return Message(sender=self.name, content="ready")

    def act(self, message: Message) -> Message:  # type: ignore[override]
        self.observed.append(message)
        return Message(sender=self.name, content=message.content.upper(), metadata=message.metadata)

    def observe(self, message: Message) -> None:  # type: ignore[override]
        self.observed.append(message)


@pytest.mark.asyncio
async def test_manager_orchestration() -> None:
    bus = MessageBus()
    worker1 = WorkerAgent("w1", bus)
    worker2 = WorkerAgent("w2", bus)
    manager = Manager({"w1": worker1, "w2": worker2}, bus=bus)

    tasks = await manager.run("alpha. beta.")

    assert [t.result for t in tasks] == ["ALPHA", "BETA"]
    assert all(t.status is TaskStatus.DONE for t in tasks)
    assert worker1.observed[0].content == "alpha"
    assert worker2.observed[0].content == "beta"


class LazyWorker(Agent):
    """Agent without preconfigured bus used for dynamic registration."""

    observed: list[Message]

    def __init__(self) -> None:
        self.observed = []

    def plan(self) -> Message:  # type: ignore[override]
        return Message(sender="lazy", content="ready")

    def act(self, message: Message) -> Message:  # type: ignore[override]
        self.observed.append(message)
        return Message(sender="lazy", content=message.content.upper(), metadata=message.metadata)

    def observe(self, message: Message) -> None:  # type: ignore[override]
        self.observed.append(message)


@pytest.mark.asyncio
async def test_dynamic_registration() -> None:
    bus = MessageBus()
    manager = Manager({}, bus=bus)
    worker = LazyWorker()
    manager.register_agent("w", worker)

    tasks = await manager.run("gamma.")

    assert [t.result for t in tasks] == ["GAMMA"]
    assert worker.observed[0].content == "gamma"
