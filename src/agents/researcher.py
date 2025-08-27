"""Researcher agent that fetches information from the web."""

from __future__ import annotations

from typing import Optional
import aiohttp

from .base import Agent


class ResearcherAgent(Agent):
    """Agent that performs simple HTTP GET requests."""

    role: str = "Researcher"
    goal: str = "Gather information from the internet"
    backstory: str = "An AI that searches the web for relevant data."
    verbose: bool = False
    allow_delegation: bool = False
    llm: str = "mistral"

    last_response: Optional[str] = None

    def plan(self) -> str:
        return "ready"

    async def act(self, url: str) -> str:
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    text = await response.text()
            text = text[:200]
            self.last_response = text
            return text
        except Exception as exc:  # pragma: no cover - network errors
            error = f"error: {exc}"
            self.last_response = error
            return error

    def observe(self, result: str) -> None:
        self.last_response = result
