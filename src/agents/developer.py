"""Developer agent responsible for basic file interactions."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from .base import Agent


class DeveloperAgent(Agent):
    """Agent that writes provided code snippets to the filesystem."""

    role: str = "Developer"
    goal: str = "Write and read files as requested"
    backstory: str = "An AI developer assisting with code tasks."
    verbose: bool = False
    allow_delegation: bool = False
    llm: str = "codellama"

    last_written: Optional[Path] = None

    def plan(self) -> str:
        return "ready"

    def act(
        self,
        *,
        path: Union[str, Path] | None = None,
        code: str = "",
        read: Union[str, Path] | None = None,
    ) -> str:
        if path is not None:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(code)
            self.last_written = p
            return f"wrote {p}"
        if read is not None:
            p = Path(read)
            try:
                return p.read_text()
            except FileNotFoundError:
                return "file not found"
        return "no action"

    def observe(self, result: str) -> None:
        if result.startswith("wrote "):
            self.last_written = Path(result.split(" ", 1)[1])
