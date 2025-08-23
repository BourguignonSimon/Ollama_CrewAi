import pathlib
import sys
import requests
import inspect
import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Message
from agents.researcher import ResearcherAgent


@pytest.mark.asyncio
async def test_researcher_act_async(monkeypatch, requests_mock):
    """ResearcherAgent.act should fetch data using a mocked HTTP response."""

    requests_mock.get("http://example.com", text="dummy response")

    class DummyResponse:
        def __init__(self, text: str) -> None:
            self._text = text

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def raise_for_status(self):
            return None

        async def text(self):
            return self._text

    class DummySession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(self, url):
            response = requests.get(url)
            return DummyResponse(response.text)

    monkeypatch.setattr(
        "agents.researcher.aiohttp.ClientSession", lambda *args, **kwargs: DummySession()
    )

    agent = ResearcherAgent()
    assert inspect.iscoroutinefunction(agent.act)
    response = await agent.act(Message(sender="tester", content="http://example.com"))
    assert response.content == "dummy response"
    assert agent.last_response == "dummy response"
