from dataclasses import dataclass
from enum import Enum
from typing import Optional

class TaskStatus(str, Enum):
    """Enumeration representing the state of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"


@dataclass(slots=True)
class Task:
    """Simple unit of work handled by agents.

    Parameters
    ----------
    id:
        Unique identifier for the task.
    description:
        Human readable description of the work to be performed.
    status:
        Current processing state of the task.
    result:
        Optional result produced after execution.
    """
    id: int
    description: str
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
