"""Manager agent orchestrating multiple specialized agents."""
from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Dict, List

from core.bus import MessageBus
from core.task import Task, TaskStatus

from .base import Agent
from .message import Message


@dataclass
class Manager(Agent):
    """Agent responsible for coordinating other agents."""

    agents: Dict[str, Agent]
    bus: MessageBus = field(default_factory=MessageBus)
    queue: asyncio.Queue[Message] = field(init=False)

    def __post_init__(self) -> None:
        # Register manager queue
        self.queue = self.bus.register("manager")
        self._results: List[Message] = []
        self._objective: str | None = None
        self._tasks: List[Task] = []
        # Ensure agents share the bus
        for name, agent in self.agents.items():
            if agent.bus is None:
                agent.bus = self.bus
            if agent.queue is None:
                agent.queue = self.bus.register(name)

    # -- Agent API -----------------------------------------------------
    def plan(self) -> Message:
        """Split the global objective into discrete :class:`Task` objects."""
        if not self._objective:
            raise ValueError("No objective set")
        descriptions = [t.strip() for t in self._objective.split(".") if t.strip()]
        self._tasks = [Task(id=i, description=d) for i, d in enumerate(descriptions, 1)]
        return Message(sender="manager", content="plan", metadata={"tasks": self._tasks})

    def act(self, message: Message) -> Message:
        """Distribute tasks round-robin to specialized agents via the bus."""
        tasks: List[Task] = message.metadata.get("tasks", []) if message.metadata else []
        agent_names = list(self.agents.keys())
        for idx, task in enumerate(tasks):
            target = agent_names[idx % len(agent_names)]
            task.status = TaskStatus.IN_PROGRESS
            self.bus.dispatch(
                target,
                Message(
                    sender="manager",
                    content=task.description,
                    metadata={"task_id": task.id},
                ),
            )
        return Message(sender="manager", content="dispatched", metadata={"tasks": tasks})

    def observe(self, message: Message) -> None:
        """Collect results produced by specialized agents and update tasks."""
        self._results.append(message)
        task_id = message.metadata.get("task_id") if message.metadata else None
        if task_id is not None:
            for task in self._tasks:
                if task.id == task_id:
                    task.status = TaskStatus.DONE
                    task.result = message.content
                    break

    # -- Orchestration -------------------------------------------------
    async def run(self, objective: str) -> List[Task]:
        """Run the orchestration process for ``objective`` and return tasks."""

        self._objective = objective
        plan_msg = self.plan()

        # Start worker loops
        workers = [asyncio.create_task(agent.handle()) for agent in self.agents.values()]

        self.act(plan_msg)

        for _ in self._tasks:
            msg = await self.queue.get()
            self.observe(msg)
            self.queue.task_done()

        for w in workers:
            w.cancel()
            with suppress(asyncio.CancelledError):
                await w

        return self._tasks
