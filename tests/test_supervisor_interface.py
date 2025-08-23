import pathlib
import sys
from typing import List

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents import manager as manager_module
from agents.manager import Manager
from core import MessageBus, TaskStatus
from supervisor import interface


class EchoAgent(Agent):
    """Agent that echoes received content in uppercase."""

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
async def test_manager_user_interface(monkeypatch) -> None:
    bus = MessageBus()
    agent = EchoAgent("worker", bus)
    manager = Manager({"worker": agent}, bus=bus)

    commands = iter(["status", None])

    def fake_read() -> str | None:
        return next(commands)

    progress_calls: List[List[TaskStatus]] = []

    def fake_display(tasks) -> None:
        progress_calls.append([t.status for t in tasks])

    dispatched = []
    original_dispatch = bus.dispatch

    def spy_dispatch(target, message):
        dispatched.append((target, message))
        original_dispatch(target, message)

    monkeypatch.setattr(interface, "read_user_command", fake_read)
    monkeypatch.setattr(interface, "display_progress", fake_display)
    # Manager imports these symbols directly; patch the manager module too
    monkeypatch.setattr(manager_module, "read_user_command", fake_read)
    monkeypatch.setattr(manager_module, "display_progress", fake_display)
    monkeypatch.setattr(bus, "dispatch", spy_dispatch)

    tasks = await manager.run("hello.")

    # User command dispatched to manager queue
    assert any(t == "manager" and m.content == "status" for t, m in dispatched)
    # Progress displayed when task updated
    assert progress_calls and progress_calls[-1][0] is TaskStatus.DONE
    assert tasks[0].result == "HELLO"
