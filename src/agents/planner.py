"""Planner agent for project decomposition."""

from __future__ import annotations

from typing import List

from .base import Agent


class PlannerAgent(Agent):
    """Agent that decomposes objectives into smaller tasks."""

    role: str = "Planner"
    goal: str = "Break down objectives into tasks"
    backstory: str = "A strategic planner that organises work."
    verbose: bool = False
    allow_delegation: bool = False
    llm: str = "llama3"

    tasks: List[str] = []

    def plan(self, objective: str) -> List[str]:
        self.tasks = [t.strip() for t in objective.split(".") if t.strip()]
        return self.tasks

    def act(self, objective: str) -> List[str]:
        return self.plan(objective)

    def observe(self, tasks: List[str]) -> None:
        self.tasks = tasks
