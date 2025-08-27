"""Tester agent for executing test suites."""

from __future__ import annotations

import subprocess
import asyncio
from typing import Optional

from .base import Agent


class TesterAgent(Agent):
    """Agent that runs shell commands such as pytest."""

    __test__ = False  # prevent pytest from collecting as a test class
    role: str = "Tester"
    goal: str = "Verify code correctness by running tests"
    backstory: str = "An AI tasked with executing test commands."
    verbose: bool = False
    allow_delegation: bool = False
    llm: str = "llama3"

    last_result: Optional[str] = None

    def plan(self) -> str:
        return "ready"

    async def act(self, command: str = "pytest") -> str:
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                command.split(),
                capture_output=True,
                text=True,
                check=True,
            )
            self.last_result = result.stdout
            return "success"
        except subprocess.CalledProcessError as exc:  # pragma: no cover - failure path
            self.last_result = exc.stderr
            return "failure"

    def observe(self, result: str) -> None:
        self.last_result = result
