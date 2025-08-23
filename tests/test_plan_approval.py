import pathlib
import sys
import asyncio

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents.manager import Manager
from core import MessageBus, TaskStatus


class RecordingAgent(Agent):
    """Agent that records messages it receives."""

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
async def test_manager_requests_plan_approval() -> None:
    bus = MessageBus()
    worker = RecordingAgent("worker", bus)
    manager = Manager({"worker": worker}, bus=bus)

    run_task = asyncio.create_task(manager.run("hello."))

    # Manager should pause awaiting approval and not dispatch tasks yet
    await asyncio.sleep(0.1)
    assert worker.observed == []
    assert not run_task.done()

    # Approve the plan
    bus.send_to_supervisor(Message(sender="supervisor", content="approve"))

    tasks = await asyncio.wait_for(run_task, timeout=1)
    assert [t.result for t in tasks] == ["HELLO"]
    assert all(t.status is TaskStatus.DONE for t in tasks)
    assert worker.observed[0].content == "hello"
