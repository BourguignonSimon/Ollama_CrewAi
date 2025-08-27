import pathlib
import sys
import requests
import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents.researcher import ResearcherAgent


@pytest.mark.asyncio
async def test_researcher_act_requests_mock(monkeypatch, requests_mock):
    """ResearcherAgent.act should fetch mocked data via requests_mock."""
    url = "http://example.com/data"
    requests_mock.get(url, text="mocked data")

    class DummyResponse:
        def __init__(self, url: str) -> None:
            self._url = url

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def raise_for_status(self) -> None:
            return None

        async def text(self) -> str:
            return requests.get(self._url).text

    class DummySession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(self, url: str) -> DummyResponse:
            return DummyResponse(url)

    monkeypatch.setattr(
        "agents.researcher.aiohttp.ClientSession", lambda *args, **kwargs: DummySession()
    )

    agent = ResearcherAgent()
    response = await agent.act(url)

    assert response == "mocked data"
    assert agent.last_response == "mocked data"
