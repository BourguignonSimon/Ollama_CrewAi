"""Manager agent orchestrating multiple specialized agents."""
from __future__ import annotations

import asyncio
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Dict, List
import logging

from core.bus import MessageBus
from core.logging import get_logger
from core.task import Task, TaskStatus
from core.policies import check_policy
from core.storage import Storage

from .base import Agent
from .message import Message


@dataclass
class Manager(Agent):
    """Agent responsible for coordinating other agents."""

    agents: Dict[str, Agent] = field(default_factory=dict)
    bus: MessageBus = field(default_factory=MessageBus)
    storage: Storage | None = None
    queue: asyncio.Queue[Message] = field(init=False)
    logger: logging.LoggerAdapter = field(default_factory=lambda: get_logger("manager"))

    def __post_init__(self) -> None:
        super().__init__(self.logger)
        # Register manager queue
        self.queue = self.bus.register("manager")
        # Ensure supervisor channel exists for UI interaction
        self.bus.register("supervisor")
        self._results: List[Message] = []
        self._objective: str | None = None
        self._tasks: List[Task] = []
        self._decisions: List[str] = []
        self._history: List[Message] = []
        # Ensure agents share the bus
        for name, agent in list(self.agents.items()):
            self.register_agent(name, agent)

    # -- Persistence ---------------------------------------------------
    def _persist(self) -> None:
        if self.storage is not None:
            self.storage.save(self._tasks, decisions=self._decisions, messages=self._history)

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
        """Split the objective into tasks and return the plan for approval."""
        if not self._objective:
            raise ValueError("No objective set")
        descriptions = [t.strip() for t in self._objective.split(".") if t.strip()]
        self._tasks = [Task(id=i, description=d) for i, d in enumerate(descriptions, 1)]
        self._persist()
        # Do not dispatch here; the plan must be approved first.
        return Message(sender="manager", content="plan", metadata={"tasks": self._tasks})

    async def request_approval(self, plan: Message) -> bool:
        """Send ``plan`` to the supervisor and await approval."""
        self.bus.send_to_supervisor(plan)
        self._history.append(plan)
        # Give the supervisor a chance to consume the plan before we start
        # waiting for the approval response to avoid racing with our own
        # message.
        await asyncio.sleep(0)
        while True:
            response = await self.bus.recv_from_supervisor()
            if response.sender == "manager" and response.content == "plan":
                # Put the plan back for the supervisor to read and yield
                # so it can be consumed before we listen again.
                self.bus.send_to_supervisor(response)
                await asyncio.sleep(0)
                continue
            self._history.append(response)
            self._decisions.append(response.content)
            self._persist()
            return response.content.lower() in {"approve", "approved", "yes"}

    def act(self, message: Message) -> Message:
        """Distribute tasks round-robin to specialized agents via the bus."""
        tasks: List[Task] = message.metadata.get("tasks", []) if message.metadata else []
        agent_names = list(self.agents.keys())
        for idx, task in enumerate(tasks):
            if not check_policy(task.description):
                task.status = TaskStatus.FAILED
                # Inform supervisor about the refusal
                refusal = Message(
                    sender="manager",
                    content="refused",
                    metadata={"task_id": task.id},
                )
                self.bus.send_to_supervisor(refusal)
                self._history.append(refusal)
                # Notify internal queue so ``run`` can progress
                self.queue.put_nowait(refusal)
                self.logger.warning("policy_refused", extra={"task": task.id})
                self._persist()
                continue
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
            self.logger.info("dispatch", extra={"task": task.id})
        self._persist()
        return Message(sender="manager", content="dispatched", metadata={"tasks": tasks})

    def observe(self, message: Message) -> None:
        """Collect results produced by specialized agents and update tasks."""
        self._results.append(message)
        task_id = message.metadata.get("task_id") if message.metadata else None
        if task_id is not None:
            for task in self._tasks:
                if task.id == task_id:
                    if message.content in {"refused", "error"}:
                        task.status = TaskStatus.FAILED
                    else:
                        task.status = TaskStatus.DONE
                        task.result = message.content
                    break
            self.logger.info("result", extra={"task": task_id})
        # Forward progress update to supervisor interface
        progress = Message(
            sender="manager",
            content="progress",
            metadata={"tasks": list(self._tasks)},
        )
        self.bus.send_to_supervisor(progress)
        self._history.append(progress)
        self._persist()

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
        approved = await self.request_approval(plan_msg)
        if not approved:
            return self._tasks

        async def _safe_handle(agent: Agent) -> None:
            try:
                await agent.handle()
            except Exception:
                for task in self._tasks:
                    if task.status is TaskStatus.IN_PROGRESS:
                        task.status = TaskStatus.FAILED
                        error = Message(
                            sender="manager",
                            content="error",
                            metadata={"task_id": task.id},
                        )
                        self.queue.put_nowait(error)
                self._persist()

        workers = [asyncio.create_task(_safe_handle(agent)) for agent in self.agents.values()]

        self.act(plan_msg)

        remaining = len(self._tasks)

        try:
            while remaining:
                try:
                    msg = await asyncio.wait_for(self.queue.get(), timeout=timeout)
                except asyncio.TimeoutError:
                    for task in self._tasks:
                        if task.status is TaskStatus.IN_PROGRESS:
                            task.status = TaskStatus.FAILED
                    self._persist()
                    break
                else:
                    if msg.sender != "user":
                        self.observe(msg)
                        remaining -= 1
                    self.queue.task_done()
        finally:
            for w in workers:
                w.cancel()
                with suppress(asyncio.CancelledError):
                    await w

        self._persist()
        return self._tasks
