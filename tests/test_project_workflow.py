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


class FailingAgent(UppercaseAgent):
    """Agent that raises an exception when handling messages."""

    async def handle(self) -> None:  # type: ignore[override]
        raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_full_mission_success() -> None:
    bus = MessageBus()
    worker = UppercaseAgent("worker", bus)
    manager = Manager({"worker": worker}, bus=bus)

    run_task = asyncio.create_task(manager.run("alpha. beta."))
    await bus.recv_from_supervisor()
    bus.send_to_supervisor(Message(sender="supervisor", content="approve"))
    tasks = await run_task

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
        run_task = asyncio.create_task(manager.run("task."))
        await bus.recv_from_supervisor()
        bus.send_to_supervisor(Message(sender="supervisor", content="approve"))
        await run_task


@pytest.mark.asyncio
async def test_invalid_message() -> None:
    bus = MessageBus()
    worker = NoMetadataAgent("worker", bus)
    manager = Manager({"worker": worker}, bus=bus)

    run_task = asyncio.create_task(manager.run("alpha."))
    await bus.recv_from_supervisor()
    bus.send_to_supervisor(Message(sender="supervisor", content="approve"))
    tasks = await run_task

    assert tasks[0].status is TaskStatus.IN_PROGRESS
    assert tasks[0].result is None


@pytest.mark.asyncio
async def test_timeout(caplog: pytest.LogCaptureFixture) -> None:
    bus = MessageBus()
    worker = SilentAgent("worker", bus)
    manager = Manager({"worker": worker}, bus=bus)
    caplog.set_level("ERROR")
    run_task = asyncio.create_task(manager.run("alpha.", timeout=0.1))
    await bus.recv_from_supervisor()
    bus.send_to_supervisor(Message(sender="supervisor", content="approve"))
    tasks = await run_task
    assert tasks[0].status is TaskStatus.FAILED
    assert any(record.message == "timeout" for record in caplog.records)


@pytest.mark.asyncio
async def test_worker_exception_logging(caplog: pytest.LogCaptureFixture) -> None:
    bus = MessageBus()
    worker = FailingAgent("worker", bus)
    manager = Manager({"worker": worker}, bus=bus)
    caplog.set_level("ERROR")
    run_task = asyncio.create_task(manager.run("alpha."))
    await bus.recv_from_supervisor()
    bus.send_to_supervisor(Message(sender="supervisor", content="approve"))
    tasks = await run_task
    assert tasks[0].status is TaskStatus.FAILED
    assert any(record.message == "worker_error" for record in caplog.records)
