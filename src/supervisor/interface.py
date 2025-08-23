from __future__ import annotations

from typing import Iterable

from core.task import Task


def read_user_command() -> str | None:
    """Read a command from the user, returning ``None`` on EOF.

    The default implementation simply wraps :func:`input` so it can be easily
    patched during testing.
    """
    try:
        cmd = input()
    except EOFError:
        return None
    cmd = cmd.strip()
    return cmd or None


def display_progress(tasks: Iterable[Task]) -> None:
    """Display progress for ``tasks``.

    This naive implementation prints each task's status. It is intended to be
    replaced or patched by a richer user interface.
    """
    for task in tasks:
        print(f"Task {task.id}: {task.status.name}")
