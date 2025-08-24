import asyncio
import pathlib
import sys

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents.manager import Manager
from core import MessageBus, TaskStatus


class ErrorAgent(Agent):
    def __init__(self, name: str, bus: MessageBus) -> None:
        self.name = name
        self.bus = bus
        self.queue = bus.register(name)

    def plan(self) -> Message:  # type: ignore[override]
        return Message(sender=self.name, content="ready")

    def act(self, message: Message) -> Message:  # type: ignore[override]
        raise RuntimeError("boom")

    def observe(self, message: Message) -> None:  # type: ignore[override]
        pass


@pytest.mark.asyncio
async def test_error_propagates_to_supervisor() -> None:
    bus = MessageBus()
    worker = ErrorAgent("worker", bus)
    manager = Manager({"worker": worker}, bus=bus)

    run_task = asyncio.create_task(manager.run("task."))
    plan = await asyncio.wait_for(bus.recv_from_supervisor(), timeout=1)
    assert plan.content == "plan"
    bus.send_to_supervisor(Message(sender="supervisor", content="approve"))

    progress = await asyncio.wait_for(bus.recv_from_supervisor(), timeout=1)
    assert progress.content == "progress"
    tasks = progress.metadata["tasks"]
    assert tasks[0].status is TaskStatus.FAILED

    await run_task
