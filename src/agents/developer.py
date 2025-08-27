"""Developer agent responsible for generating and saving code."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from langchain_ollama import OllamaLLM

from .base import Agent


class DeveloperAgent(Agent):
    """Agent that uses an LLM to generate code and optionally save it."""

    last_written: Optional[Path] = None

    def __init__(
        self,
        *,
        role: str = "Developer",
        goal: str = "Write and read files as requested",
        backstory: str = "An AI developer assisting with code tasks.",
        model: str = "codellama",
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
        self.last_written = None

    def plan(self) -> str:
        return "ready"

    def act(
        self,
        prompt: str,
        *,
        path: Union[str, Path] | None = None,
    ) -> str:
        """Generate code from ``prompt`` and optionally write to ``path``."""
        code = self.llm.invoke(prompt)
        if path is not None:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(code)
            self.last_written = p
        return code

    def observe(self, result: str) -> None:
        try:
            p = Path(result)
        except TypeError:  # pragma: no cover - non-path input
            return
        if p.exists():
            self.last_written = p
