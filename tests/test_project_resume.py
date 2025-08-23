import asyncio
import pathlib
import sys

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents.manager import Manager
from core import MessageBus, Storage, TaskStatus


class EchoAgent(Agent):
    """Agent that returns uppercase messages."""

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
async def test_save_and_resume(tmp_path):
    bus = MessageBus()
    storage = Storage(tmp_path / "state.json")
    worker = EchoAgent("worker", bus)
    manager = Manager({"worker": worker}, bus=bus, storage=storage)

    run_task = asyncio.create_task(manager.run("alpha."))
    plan = await bus.recv_from_supervisor()
    assert plan.content == "plan"
    bus.send_to_supervisor(Message(sender="supervisor", content="approve"))
    tasks = await run_task

    assert tasks[0].status is TaskStatus.DONE
    assert tasks[0].result == "ALPHA"

    loaded_tasks, _, decisions, messages = storage.load()
    assert loaded_tasks == tasks
    assert decisions == ["approve"]
    assert any(m.content == "progress" for m in messages)
    # First message should be the plan sent to supervisor
    assert messages[0].content == "plan"
