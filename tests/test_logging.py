import asyncio
import logging
from contextlib import suppress

from core.bus import MessageBus
from core.logging import get_logger
from agents.developer import DeveloperAgent
from agents.message import Message


def test_agent_logging(caplog):
    bus = MessageBus()
    bus.register("manager")
    agent = DeveloperAgent(bus=bus, logger=get_logger("developer"))

    async def run_agent():
        task = asyncio.create_task(agent.handle())
        bus.dispatch("developer", Message(sender="manager", content="", metadata={"task_id": 1}))
        await asyncio.sleep(0.05)
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

    with caplog.at_level(logging.INFO):
        asyncio.run(run_agent())

    assert any(r.agent == "developer" and r.task == 1 for r in caplog.records)
