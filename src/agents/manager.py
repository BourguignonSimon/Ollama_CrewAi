"""Manager agent orchestrating multiple specialized agents."""

from __future__ import annotations

from typing import Dict, List, Tuple

from .base import Agent


class Manager(Agent):
    """Simple manager that distributes tasks to other agents."""

    role: str = "Manager"
    goal: str = "Coordinate agents to accomplish objectives"
    backstory: str = "Oversees project execution and integrates results."
    verbose: bool = False
    allow_delegation: bool = True
    llm: str = "llama3"

    def __init__(self, agents: Dict[str, Agent] | None = None) -> None:
        super().__init__()
        self.agents: Dict[str, Agent] = agents or {}
        self.tasks: List[str] = []
        self.results: List[Tuple[str, str]] = []

    def plan(self, objective: str) -> List[str]:
        self.tasks = [t.strip() for t in objective.split(".") if t.strip()]
        return self.tasks

    def act(self, objective: str) -> List[Tuple[str, str]]:
        tasks = self.plan(objective)
        agent_names = list(self.agents.keys())
        results: List[Tuple[str, str]] = []
        for idx, task in enumerate(tasks):
            agent = self.agents[agent_names[idx % len(agent_names)]]
            response = agent.act(task)
            agent.observe(response)
            results.append((task, response))
        self.results = results
        return results

    def observe(self, results: List[Tuple[str, str]]) -> None:
        self.results = results
