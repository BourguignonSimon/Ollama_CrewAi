import pathlib
import sys

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents.planner import PlannerAgent


class StubLLM:
    def __init__(self, output: str) -> None:
        self.output = output
        self.last_prompt: str | None = None

    def invoke(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.output


def test_planner_decomposes_tasks():
    planner = PlannerAgent()
    planner.llm = StubLLM("1. alpha\n2. beta")
    response = planner.act("plan something")
    assert response == ["alpha", "beta"]
    planner.observe(response)
    assert planner.tasks == ["alpha", "beta"]
