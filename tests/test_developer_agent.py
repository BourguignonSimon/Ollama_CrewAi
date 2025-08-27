import pathlib
import sys

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents.developer import DeveloperAgent


class StubLLM:
    def __init__(self, output: str) -> None:
        self.output = output
        self.last_prompt: str | None = None

    def invoke(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.output


def test_developer_generates_code(tmp_path):
    developer = DeveloperAgent()
    developer.llm = StubLLM("print('hi')")
    target = tmp_path / "example.py"

    code = developer.act("Write a hello program", path=target)

    assert code == "print('hi')"
    assert target.read_text() == "print('hi')"
    assert developer.last_written == target
