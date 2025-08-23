"""Example of creating and registering a custom agent."""

from __future__ import annotations

import asyncio

from agents.base import Agent
from agents.manager import Manager
from agents.message import Message


class EchoAgent(Agent):
    """Agent that uppercases any received task."""

    def plan(self) -> Message:  # type: ignore[override]
        return Message(sender="echo", content="ready")

    def act(self, message: Message) -> Message:  # type: ignore[override]
        return Message(sender="echo", content=message.content.upper(), metadata=message.metadata)

    def observe(self, message: Message) -> None:  # type: ignore[override]
        print(f"EchoAgent observed: {message.content}")


async def main() -> None:
    manager = Manager()
    manager.register_agent("echo", EchoAgent())
    tasks = await manager.run("salut.")
    for task in tasks:
        print(f"Task {task.id}: {task.result}")


if __name__ == "__main__":
    asyncio.run(main())
