"""Manager agent orchestrating multiple specialized agents."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .base import Agent
from .message import Message


@dataclass
class Manager(Agent):
    """Agent responsible for coordinating other agents.

    Parameters
    ----------
    agents:
        Mapping of agent names to agent instances that will receive tasks.
    """

    agents: Dict[str, Agent]

    def __post_init__(self) -> None:
        self._queue: asyncio.Queue[Tuple[str, Message]] = asyncio.Queue()
        self._results: List[Message] = []
        self._objective: str | None = None

    # -- Agent API -----------------------------------------------------
    def plan(self) -> Message:  # type: ignore[override]
        """Split the global objective into discrete tasks."""
        if not self._objective:
            raise ValueError("No objective set")

        tasks = [t.strip() for t in self._objective.split(".") if t.strip()]
        return Message(sender="manager", content="plan", metadata={"tasks": tasks})

    def act(self, message: Message) -> Message:  # type: ignore[override]
        """Distribute tasks round-robin to specialized agents."""
        tasks: List[str] = message.metadata.get("tasks", []) if message.metadata else []
        agent_names = list(self.agents.keys())
        for idx, task in enumerate(tasks):
            target = agent_names[idx % len(agent_names)]
            self._queue.put_nowait((target, Message(sender="manager", content=task)))
        return Message(sender="manager", content="dispatched", metadata={"tasks": tasks})

    def observe(self, message: Message) -> None:  # type: ignore[override]
        """Collect results produced by specialized agents."""
        self._results.append(message)

    # -- Orchestration -------------------------------------------------
    async def run(self, objective: str) -> List[Message]:
        """Run the orchestration process for ``objective``.

        The objective is split into tasks, dispatched to agents and results
        collected. Returns the list of responses from agents.
        """

        self._objective = objective
        plan_msg = self.plan()
        self.act(plan_msg)
        await self._process_queue()
        return self._results

    async def _process_queue(self) -> None:
        while not self._queue.empty():
            target, message = await self._queue.get()
            agent = self.agents[target]
            response = agent.act(message)
            agent.observe(response)
            self.observe(response)
            self._queue.task_done()
