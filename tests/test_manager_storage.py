import asyncio
import pathlib
import sys

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents.manager import Manager
from core import MessageBus, Storage, Task, TaskStatus


class EchoAgent(Agent):
    """Agent that returns uppercase messages and records observations."""

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
async def test_resume_tasks_from_storage(tmp_path):
    bus = MessageBus()
    storage = Storage(tmp_path / "state.json")
    worker = EchoAgent("worker", bus)

    tasks = [
        Task(id=1, description="alpha", status=TaskStatus.DONE, result="ALPHA"),
        Task(id=2, description="beta"),
    ]
    storage.save(tasks)

    manager = Manager({"worker": worker}, bus=bus, storage=storage)
    assert manager._tasks == tasks

    run_task = asyncio.create_task(manager.run("resume"))
    # No approval needed; manager immediately dispatches pending tasks
    finished_tasks = await run_task

    assert finished_tasks[0].result == "ALPHA"
    assert finished_tasks[0].status is TaskStatus.DONE
    assert finished_tasks[1].result == "BETA"
    assert finished_tasks[1].status is TaskStatus.DONE
    # Only the pending task was dispatched
    assert worker.observed[0].content == "beta"
    assert all(m.content != "alpha" for m in worker.observed)

    reloaded, _, _, _ = storage.load()
    assert reloaded == finished_tasks
