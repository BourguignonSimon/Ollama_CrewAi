import asyncio
import pathlib
import sys

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents.manager import Manager
from core import MessageBus, TaskStatus
from cli import run_supervised
from supervisor import interface


@pytest.mark.asyncio
async def test_cancel_command(monkeypatch) -> None:
    bus = MessageBus()
    manager = Manager({}, bus=bus)
    monkeypatch.setattr(interface, "read_user_command", lambda: "cancel")
    monkeypatch.setattr(interface, "display_progress", lambda tasks: None)
    tasks = await run_supervised(manager, "do something.")
    assert all(t.status is TaskStatus.PENDING for t in tasks)


@pytest.mark.asyncio
async def test_unknown_command(monkeypatch) -> None:
    bus = MessageBus()
    manager = Manager({}, bus=bus)
    monkeypatch.setattr(interface, "read_user_command", lambda: "foobar")
    monkeypatch.setattr(interface, "display_progress", lambda tasks: None)
    tasks = await run_supervised(manager, "another task.")
    assert all(t.status is TaskStatus.PENDING for t in tasks)
