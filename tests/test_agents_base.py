import pathlib
import sys

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent


class DummyAgent(Agent):
    """Simple concrete implementation of :class:`Agent` used for testing."""

    role: str = "Dummy"
    goal: str = "Demonstrate behaviour"
    backstory: str = "A placeholder agent for tests."
    verbose: bool = False
    allow_delegation: bool = False
    llm: str = "test-llm"
    observed: list[str] = []

    def plan(self) -> str:  # type: ignore[override]
        return "plan"

    def act(self, message: str) -> str:  # type: ignore[override]
        return message.upper()

    def observe(self, message: str) -> None:  # type: ignore[override]
        self.observed.append(message)


def test_concrete_agent_behaviour() -> None:
    agent = DummyAgent()
    assert agent.plan() == "plan"
    response = agent.act("hello")
    assert response == "HELLO"
    agent.observe(response)
    assert agent.observed[-1] == response
