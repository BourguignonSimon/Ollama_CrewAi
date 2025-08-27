"""Writer agent for generating documentation."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Union

from .base import Agent


class WriterAgent(Agent):
    """Agent that writes documentation files to the filesystem."""

    role: str = "Writer"
    goal: str = "Produce documentation files"
    backstory: str = "An AI writer creating project docs."
    verbose: bool = False
    allow_delegation: bool = False
    llm: str = "llama3"

    documents: Dict[Path, str] = {}

    def plan(self) -> str:
        return "ready"

    def act(self, *, path: Union[str, Path] | None = None, text: str = "") -> str:
        if path is None:
            return "no document"
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        self.documents[p] = text
        return f"wrote {p}"

    def observe(self, result: str) -> None:
        if result.startswith("wrote "):
            p = Path(result.split(" ", 1)[1])
            try:
                self.documents[p] = p.read_text()
            except FileNotFoundError:  # pragma: no cover - file missing
                self.documents[p] = ""
