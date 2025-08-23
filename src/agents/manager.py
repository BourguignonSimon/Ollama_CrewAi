"""Manager agent orchestrating multiple specialized agents."""
from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Dict, List

from core.bus import MessageBus
from core.task import Task, TaskStatus
from supervisor import display_progress, read_user_command

from .base import Agent
from .message import Message


@dataclass
class Manager(Agent):
    """Agent responsible for coordinating other agents."""

    agents: Dict[str, Agent] = field(default_factory=dict)
    bus: MessageBus = field(default_factory=MessageBus)
    queue: asyncio.Queue[Message] = field(init=False)

    def __post_init__(self) -> None:
        # Register manager queue
        self.queue = self.bus.register("manager")
        self._results: List[Message] = []
        self._objective: str | None = None
        self._tasks: List[Task] = []
        # Ensure agents share the bus
        for name, agent in list(self.agents.items()):
            self.register_agent(name, agent)

    # -- Registration --------------------------------------------------
    def register_agent(self, name: str, agent: Agent) -> None:
        """Register ``agent`` under ``name`` and connect it to the bus."""
        self.agents[name] = agent
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
            display_progress(self._tasks)

    # -- Orchestration -------------------------------------------------
    async def run(self, objective: str, timeout: float | None = None) -> List[Task]:
        """Run the orchestration process for ``objective`` and return tasks.

        Parameters
        ----------
        objective:
            The overall goal the manager should execute.
        timeout:
            Optional maximum time in seconds to wait for results from
            workers. If exceeded, all incomplete tasks are marked as
            :class:`~core.task.TaskStatus.FAILED`.
        """

        self._objective = objective
        plan_msg = self.plan()

        async def _safe_handle(agent: Agent) -> None:
            try:
                await agent.handle()
            except Exception:
                for task in self._tasks:
                    if task.status is TaskStatus.IN_PROGRESS:
                        task.status = TaskStatus.FAILED

        # Start worker loops
        workers = [asyncio.create_task(_safe_handle(agent)) for agent in self.agents.values()]

        async def _user_commands() -> None:
            while True:
                cmd = await asyncio.to_thread(read_user_command)
                if cmd:
                    self.bus.dispatch("manager", Message(sender="user", content=cmd))

        user_task = asyncio.create_task(_user_commands())

        self.act(plan_msg)

        try:
            while any(task.status is TaskStatus.IN_PROGRESS for task in self._tasks):
                try:
                    msg = await asyncio.wait_for(self.queue.get(), timeout=timeout)
                except asyncio.TimeoutError:
                    for task in self._tasks:
                        if task.status is TaskStatus.IN_PROGRESS:
                            task.status = TaskStatus.FAILED
                    break
                else:
                    if msg.metadata and msg.metadata.get("task_id") is not None:
                        self.observe(msg)
                        self.queue.task_done()
        finally:
            user_task.cancel()
            with suppress(asyncio.CancelledError):
                await user_task

            for w in workers:
                w.cancel()
                with suppress(asyncio.CancelledError):
                    await w

        return self._tasks
