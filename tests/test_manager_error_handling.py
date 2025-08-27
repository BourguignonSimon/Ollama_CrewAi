import asyncio
import pathlib
import sys
from contextlib import suppress
import logging

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents.manager import Manager
from core import MessageBus, TaskStatus
from core.logging import get_logger


class ErrorAgent(Agent):
    def __init__(self, name: str, bus: MessageBus) -> None:
        self.name = name
        self.bus = bus
        self.queue = bus.register(name)
        super().__init__(get_logger(name))

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


@pytest.mark.asyncio
async def test_worker_error_sends_failure_and_logs(caplog) -> None:
    caplog.set_level(logging.ERROR)
    bus = MessageBus()
    manager_queue = bus.register("manager")
    worker = ErrorAgent("worker", bus)
    handle_task = asyncio.create_task(worker.handle())

    await bus.send("worker", Message(sender="manager", content="task", metadata={"task_id": 1}))

    failure = await asyncio.wait_for(manager_queue.get(), timeout=1)
    assert failure.content == "error"
    assert failure.metadata == {"task_id": 1}
    assert any("error" in r.getMessage() and r.exc_info for r in caplog.records)

    handle_task.cancel()
    with suppress(asyncio.CancelledError):
        await handle_task
