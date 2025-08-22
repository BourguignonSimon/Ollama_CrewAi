import pathlib
import sys

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Agent, Message


class DummyAgent(Agent):
    """Simple concrete implementation of :class:`Agent` used for testing."""

    def __init__(self) -> None:
        self.observed: list[Message] = []

    def plan(self) -> Message:  # type: ignore[override]
        return Message(sender="dummy", content="plan")

    def act(self, message: Message) -> Message:  # type: ignore[override]
        return Message(sender="dummy", content=message.content.upper())

    def observe(self, message: Message) -> None:  # type: ignore[override]
        self.observed.append(message)


def test_agent_is_abstract() -> None:
    with pytest.raises(TypeError):
        Agent()  # type: ignore[abstract]


def test_concrete_agent_behaviour() -> None:
    agent = DummyAgent()
    plan_msg = agent.plan()
    assert isinstance(plan_msg, Message)
    response = agent.act(Message(sender="tester", content="hello"))
    assert response.content == "HELLO"
    agent.observe(response)
    assert agent.observed[-1] == response


def test_message_dataclass() -> None:
    message = Message(sender="alice", content="hello", metadata={"time": 1})
    assert message.sender == "alice"
    assert message.metadata == {"time": 1}
