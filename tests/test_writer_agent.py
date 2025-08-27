import pathlib
import sys

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents.writer import WriterAgent


class StubLLM:
    def __init__(self, output: str) -> None:
        self.output = output
        self.last_prompt: str | None = None

    def invoke(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.output


def test_writer_act_creates_file_and_updates_documents(tmp_path):
    """WriterAgent.act should generate file via LLM and store it."""
    agent = WriterAgent()
    agent.llm = StubLLM("hello")
    file_path = tmp_path / "docs" / "output.txt"

    text = agent.act("Write greeting", path=file_path)

    assert file_path.read_text() == "hello"
    assert agent.documents[file_path] == "hello"
    assert text == "hello"


def test_writer_observe_updates_documents(tmp_path):
    """observe should record paths mentioned in messages."""
    agent = WriterAgent()
    agent.llm = StubLLM("unused")
    file_path = tmp_path / "docs" / "extra.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("more text")

    agent.observe(file_path)

    assert agent.documents[file_path] == "more text"
