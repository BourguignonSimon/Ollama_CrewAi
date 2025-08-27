import pathlib
import sys

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents.planner import PlannerAgent


def test_planner_decomposes_tasks():
    planner = PlannerAgent()
    response = planner.act("alpha. beta.")
    assert response == ["alpha", "beta"]
    planner.observe(response)
    assert planner.tasks == ["alpha", "beta"]
