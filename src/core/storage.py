"""Persistence utilities for tasks and agent states."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

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
    """Simple JSON based storage for tasks and agent states."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def save(self, tasks: List[Task], agent_states: Dict[str, Dict[str, Any]]) -> None:
        """Persist ``tasks`` and ``agent_states`` to disk."""
        data = {
            "tasks": [task_to_dict(t) for t in tasks],
            "agents": agent_states,
        }
        self.path.write_text(json.dumps(data, indent=2))

    def load(self) -> Tuple[List[Task], Dict[str, Dict[str, Any]]]:
        """Load tasks and agent states from disk."""
        if not self.path.exists():
            return [], {}
        raw = json.loads(self.path.read_text())
        tasks = [task_from_dict(t) for t in raw.get("tasks", [])]
        agents = raw.get("agents", {})
        return tasks, agents
