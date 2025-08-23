import pathlib
import sys
import inspect
import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Message
from agents.tester import TesterAgent


@pytest.mark.asyncio
async def test_tester_act_async(monkeypatch):
    """TesterAgent.act should run subprocess in a thread and be async."""

    def fake_run(cmd, capture_output, text, check):
        class Result:
            stdout = "ok"
            stderr = ""
        return Result()

    monkeypatch.setattr("agents.tester.subprocess.run", fake_run)

    agent = TesterAgent()
    assert inspect.iscoroutinefunction(agent.act)
    response = await agent.act(Message(sender="manager", content="echo hi"))
    assert response.content == "success"
    assert response.metadata["output"] == "ok"
    assert agent.last_result == "ok"
