import pathlib
import sys

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Message
from agents.planner import PlannerAgent


def test_planner_decomposes_tasks():
    planner = PlannerAgent()
    msg = Message(sender="tester", content="alpha. beta.")
    response = planner.act(msg)

    assert response.metadata["tasks"] == ["alpha", "beta"]
    planner.observe(response)
    assert planner.tasks == ["alpha", "beta"]
    assert "planning" in planner.capabilities
