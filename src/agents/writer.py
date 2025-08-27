"""Writer agent for generating documentation."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Union

from langchain_ollama import OllamaLLM

from .base import Agent


class WriterAgent(Agent):
    """Agent that uses an LLM to generate documentation and save it."""

    documents: Dict[Path, str] = {}

    def __init__(
        self,
        *,
        role: str = "Writer",
        goal: str = "Produce documentation files",
        backstory: str = "An AI writer creating project docs.",
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
        self.documents = {}

    def plan(self) -> str:
        return "ready"

    def act(
        self,
        prompt: str,
        *,
        path: Union[str, Path] | None = None,
    ) -> str:
        text = self.llm.invoke(prompt)
        if path is not None:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
            self.documents[p] = text
        return text

    def observe(self, path: Union[str, Path]) -> None:
        p = Path(path)
        try:
            self.documents[p] = p.read_text()
        except FileNotFoundError:  # pragma: no cover - file missing
            self.documents[p] = ""
