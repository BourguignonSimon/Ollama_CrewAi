import pathlib
import sys
import asyncio

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message
from agents.manager import Manager
from core import MessageBus, TaskStatus


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
async def test_bus_supervisor_channel_basic() -> None:
    bus = MessageBus()
    msg = Message(sender="tester", content="ping")
    bus.send_to_supervisor(msg)
    received = await bus.recv_from_supervisor()
    assert received.content == "ping"
    assert received.sender == "tester"


@pytest.mark.asyncio
async def test_manager_reports_progress_via_supervisor_queue() -> None:
    bus = MessageBus()
    agent = EchoAgent("worker", bus)
    manager = Manager({"worker": agent}, bus=bus)

    manager_task = asyncio.create_task(manager.run("hello."))

    # Manager first sends the plan for approval
    plan = await asyncio.wait_for(bus.recv_from_supervisor(), timeout=2)
    assert plan.content == "plan"

    # Approve the plan so the manager can proceed
    bus.send_to_supervisor(Message(sender="supervisor", content="approve"))
    await asyncio.sleep(0)

    progress = await asyncio.wait_for(bus.recv_from_supervisor(), timeout=2)
    assert progress.sender == "manager"
    tasks = progress.metadata["tasks"]
    assert tasks[0].status is TaskStatus.DONE
    assert tasks[0].result == "HELLO"

    await manager_task
