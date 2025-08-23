"""Persistence utilities for tasks, decisions and messages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from agents.message import Message

from .task import Task, TaskStatus


def task_to_dict(task: Task) -> Dict[str, Any]:
    """Convert a :class:`Task` into a serialisable dictionary."""
    return {
        "id": task.id,
        "description": task.description,
        "status": task.status.value,
        "result": task.result,
    }


def task_from_dict(data: Dict[str, Any]) -> Task:
    """Reconstruct a :class:`Task` from a dictionary."""
    return Task(
        id=data["id"],
        description=data["description"],
        status=TaskStatus(data["status"]),
        result=data.get("result"),
    )


class Storage:
    """Simple JSON based storage for tasks and agent communication."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    # ------------------------------------------------------------------
    def save(
        self,
        tasks: List[Task],
        agent_states: Dict[str, Dict[str, Any]] | None = None,
        decisions: List[str] | None = None,
        messages: List[Message] | None = None,
    ) -> None:
        """Persist framework state to disk.

        Parameters
        ----------
        tasks:
            List of current tasks.
        agent_states:
            Optional mapping of agent specific state data.
        decisions:
            Decisions exchanged between supervisor and manager.
        messages:
            Messages exchanged between supervisor and manager.
        """

        def message_to_dict(message: Message) -> Dict[str, Any]:
            metadata = message.metadata
            if metadata and "tasks" in metadata:
                metadata = dict(metadata)
                metadata["tasks"] = [task_to_dict(t) for t in metadata["tasks"]]
            return {
                "sender": message.sender,
                "content": message.content,
                "metadata": metadata,
            }

        data = {
            "tasks": [task_to_dict(t) for t in tasks],
            "agents": agent_states or {},
            "decisions": decisions or [],
            "messages": [message_to_dict(m) for m in messages or []],
        }
        self.path.write_text(json.dumps(data, indent=2))

    # ------------------------------------------------------------------
    def load(
        self,
        ) -> Tuple[
            List[Task],
            Dict[str, Dict[str, Any]],
            List[str],
            List[Message],
        ]:
        """Load tasks, agent states, decisions and messages from disk."""

        def message_from_dict(data: Dict[str, Any]) -> Message:
            metadata = data.get("metadata")
            if metadata and "tasks" in metadata:
                metadata = dict(metadata)
                metadata["tasks"] = [task_from_dict(t) for t in metadata["tasks"]]
            return Message(
                sender=data["sender"],
                content=data["content"],
                metadata=metadata,
            )

        if not self.path.exists():
            return [], {}, [], []
        raw = json.loads(self.path.read_text())
        tasks = [task_from_dict(t) for t in raw.get("tasks", [])]
        agents = raw.get("agents", {})
        decisions = raw.get("decisions", [])
        messages = [message_from_dict(m) for m in raw.get("messages", [])]
        return tasks, agents, decisions, messages
