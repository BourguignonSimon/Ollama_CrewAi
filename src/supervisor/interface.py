"""User interface helpers for supervisor interactions."""
from __future__ import annotations

from typing import Iterable

from core.task import Task


def read_user_command() -> str | None:
    """Read a user command if available.

    Returns ``None`` when no more commands are available (e.g. EOF).
    """
    try:
        return input()
    except (EOFError, OSError):
        # ``OSError`` is raised under pytest's stdin capture; treat it as EOF.
        return None


def display_progress(tasks: Iterable[Task]) -> None:
    """Display current progress for ``tasks``.

    This simple implementation prints each task's status. The function is kept
    minimal so tests can monkeypatch it.
    """
    for task in tasks:
        print(f"{task.id}. {task.description} - {task.status.name}")
