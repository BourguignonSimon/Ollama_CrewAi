import asyncio
import pathlib
import sys

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents.manager import Manager
from core import MessageBus, TaskStatus
import core.policies as policies


class EchoAgent(Agent):
    """Agent that echoes back received messages."""

    def __init__(self, name: str, bus: MessageBus) -> None:
        self.name = name
        self.bus = bus
        self.queue = bus.register(name)
        self.observed: list[Message] = []

    def plan(self) -> Message:  # type: ignore[override]
        return Message(sender=self.name, content="ready")

    def act(self, message: Message) -> Message:  # type: ignore[override]
        self.observed.append(message)
        return Message(sender=self.name, content=message.content, metadata=message.metadata)

    def observe(self, message: Message) -> None:  # type: ignore[override]
        self.observed.append(message)


@pytest.mark.asyncio
async def test_refusal_on_policy_violation(monkeypatch) -> None:
    bus = MessageBus()
    worker = EchoAgent("worker", bus)
    manager = Manager({"worker": worker}, bus=bus)

    # Restrict allowed commands to a single safe value
    monkeypatch.setattr(policies, "ALLOWED_COMMANDS", {"echo"})

    run_task = asyncio.create_task(manager.run("rm secret."))
    plan = await asyncio.wait_for(bus.recv_from_supervisor(), timeout=1)
    assert plan.content == "plan"
    bus.send_to_supervisor(Message(sender="supervisor", content="approve"))

    # Manager should refuse the task before any worker processes it
    refusal = await asyncio.wait_for(bus.recv_from_supervisor(), timeout=1)
    assert refusal.content == "refused"

    tasks = await run_task
    assert tasks[0].status is TaskStatus.FAILED
    assert worker.observed == []
