import pathlib
import sys
from typing import Iterator

import pytest
from unittest.mock import MagicMock

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents.manager import Manager
from core import MessageBus, TaskStatus
from agents import manager as manager_module


class EchoAgent(Agent):
    def __init__(self, name: str, bus: MessageBus) -> None:
        self.name = name
        self.bus = bus
        self.queue = bus.register(name)

    def plan(self) -> Message:  # type: ignore[override]
        return Message(sender=self.name, content="ready")

    async def act(self, message: Message) -> Message:  # type: ignore[override]
        import asyncio

        await asyncio.sleep(0.1)
        return Message(sender=self.name, content=message.content.upper(), metadata=message.metadata)

    def observe(self, message: Message) -> None:  # type: ignore[override]
        pass


@pytest.mark.asyncio
async def test_supervisor_interface_interaction(monkeypatch: pytest.MonkeyPatch) -> None:
    bus = MessageBus()
    worker = EchoAgent("w", bus)
    manager = Manager({"w": worker}, bus=bus)

    commands: Iterator[str] = iter(["pause"])

    def fake_read() -> str:
        return next(commands, "")

    mock_display = MagicMock()
    mock_dispatch = MagicMock(wraps=bus.dispatch)

    monkeypatch.setattr(manager_module, "read_user_command", fake_read)
    monkeypatch.setattr(manager_module, "display_progress", mock_display)
    monkeypatch.setattr(bus, "dispatch", mock_dispatch)

    tasks = await manager.run("alpha.")

    assert any(call.args[1].content == "pause" for call in mock_dispatch.call_args_list)
    mock_display.assert_called()
    assert all(t.status is TaskStatus.DONE for t in tasks)
