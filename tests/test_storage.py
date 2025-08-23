import pathlib
import sys

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from core import Storage, Task, TaskStatus


def test_save_and_load(tmp_path):
    storage = Storage(tmp_path / "state.json")

    tasks = [
        Task(id=1, description="alpha", status=TaskStatus.DONE, result="A"),
        Task(id=2, description="beta"),
    ]
    agent_states = {"agent1": {"count": 3}, "agent2": {"status": "idle"}}

    storage.save(tasks, agent_states)
    loaded_tasks, loaded_agents, loaded_decisions, loaded_messages = storage.load()

    assert loaded_tasks == tasks
    assert loaded_agents == agent_states
    assert loaded_decisions == []
    assert loaded_messages == []
    assert loaded_tasks[0].status is TaskStatus.DONE
    assert loaded_tasks[1].status is TaskStatus.PENDING
