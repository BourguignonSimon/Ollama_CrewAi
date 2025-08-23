import asyncio
import pathlib
import sys

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import cli  # type: ignore
from agents.message import Message
from core.task import TaskStatus
from core import policies


def test_full_team_run(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        policies,
        "ALLOWED_COMMANDS",
        {"plan", "code", "write", "echo", "research"},
    )
    monkeypatch.setattr(policies, "NETWORK_ACCESS", True)

    cfg = {
        "objective": "plan tasks. code feature. write docs. echo hi. research example.",
        "agents": {
            "planner": {},
            "developer": {},
            "writer": {},
            "tester": {},
            "researcher": {},
        },
    }
    manager = cli.build_manager(cfg)

    async def orchestrate():
        run_task = asyncio.create_task(manager.run(cfg["objective"]))
        plan = await asyncio.wait_for(manager.bus.recv_from_supervisor(), timeout=1)
        assert plan.content == "plan"
        manager.bus.send_to_supervisor(Message(sender="supervisor", content="approve"))
        return await run_task

    tasks = asyncio.run(orchestrate())
    assert len(tasks) == 5
    assert all(t.status is TaskStatus.DONE for t in tasks)
    assert tasks[3].result == "success"
    assert tasks[4].result.startswith("error")
