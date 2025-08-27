"""Planner agent for project decomposition."""

from __future__ import annotations

from typing import List

from langchain_ollama import OllamaLLM

from .base import Agent


class PlannerAgent(Agent):
    """Agent that uses an LLM to break objectives into tasks."""

    tasks: List[str] = []

    def __init__(
        self,
        *,
        role: str = "Planner",
        goal: str = "Break down objectives into tasks",
        backstory: str = "A strategic planner that organises work.",
        model: str = "llama3",
        llm: OllamaLLM | None = None,
        verbose: bool = False,
        allow_delegation: bool = False,
    ) -> None:
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm or OllamaLLM(model=model),
            verbose=verbose,
            allow_delegation=allow_delegation,
        )
        self.tasks = []

    def plan(self, objective: str) -> List[str]:
        plan_text = self.llm.invoke(objective)
        self.tasks = [t.strip().lstrip("-0123456789. ") for t in plan_text.splitlines() if t.strip()]
        return self.tasks

    def act(self, objective: str) -> List[str]:
        return self.plan(objective)

    def observe(self, tasks: List[str]) -> None:
        self.tasks = tasks
