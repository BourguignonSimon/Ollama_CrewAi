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

    called: dict[str, object] = {}

    async def fake_to_thread(func, *args, **kwargs):
        called["func"] = func
        return func(*args, **kwargs)

    monkeypatch.setattr("agents.tester.subprocess.run", fake_run)
    monkeypatch.setattr("agents.tester.asyncio.to_thread", fake_to_thread)

    agent = TesterAgent()
    assert inspect.iscoroutinefunction(agent.act)
    response = await agent.act(Message(sender="manager", content="echo hi"))
    assert called["func"] is fake_run
    assert response.content == "success"
    assert response.metadata["output"] == "ok"
    assert agent.last_result == "ok"
