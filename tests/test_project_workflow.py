import asyncio
import pathlib
import sys

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents.manager import Manager
from core import MessageBus, TaskStatus


class UppercaseAgent(Agent):
    """Agent that echoes back messages in uppercase."""

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


class NoMetadataAgent(Agent):
    """Agent that drops metadata before responding, simulating invalid messages."""

    def __init__(self, name: str, bus: MessageBus) -> None:
        self.name = name
        self.bus = bus
        self.queue = bus.register(name)

    def plan(self) -> Message:  # type: ignore[override]
        return Message(sender=self.name, content="ready")

    def act(self, message: Message) -> Message:  # type: ignore[override]
        return Message(sender=self.name, content=message.content.upper())

    def observe(self, message: Message) -> None:  # type: ignore[override]
        pass

    async def handle(self) -> None:  # type: ignore[override]
        if not self.bus or not self.queue:
            raise RuntimeError("Agent is not connected to a message bus")
        while True:
            message = await self.queue.get()
            response = self.act(message)
            self.observe(response)
            # Intentionally omit metadata to simulate an invalid message
            await self.bus.send("manager", response)
            self.queue.task_done()


class SilentAgent(UppercaseAgent):
    """Agent that never processes incoming messages, causing timeouts."""

    async def handle(self) -> None:  # type: ignore[override]
        return


@pytest.mark.asyncio
async def test_full_mission_success() -> None:
    bus = MessageBus()
    worker = UppercaseAgent("worker", bus)
    manager = Manager({"worker": worker}, bus=bus)

    tasks = await manager.run("alpha. beta.")

    assert [t.result for t in tasks] == ["ALPHA", "BETA"]
    assert all(t.status is TaskStatus.DONE for t in tasks)


@pytest.mark.asyncio
async def test_agent_unavailable() -> None:
    bus = MessageBus()
    worker = UppercaseAgent("worker", bus)
    manager = Manager({"worker": worker}, bus=bus)

    # Simulate agent becoming unavailable by removing its queue from the bus
    bus._queues.pop("worker")

    with pytest.raises(KeyError):
        await manager.run("task.")


@pytest.mark.asyncio
async def test_invalid_message() -> None:
    bus = MessageBus()
    worker = NoMetadataAgent("worker", bus)
    manager = Manager({"worker": worker}, bus=bus)

    tasks = await manager.run("alpha.")

    assert tasks[0].status is TaskStatus.IN_PROGRESS
    assert tasks[0].result is None


@pytest.mark.asyncio
async def test_timeout() -> None:
    bus = MessageBus()
    worker = SilentAgent("worker", bus)
    manager = Manager({"worker": worker}, bus=bus)

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(manager.run("alpha."), timeout=0.1)
