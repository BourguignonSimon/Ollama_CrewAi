import pathlib
import sys

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Message
from agents.writer import WriterAgent


def test_writer_act_creates_file_and_updates_documents(tmp_path):
    """WriterAgent.act should write file and store it in documents dict."""
    agent = WriterAgent()
    file_path = tmp_path / "docs" / "output.txt"
    message = Message(sender="tester", content="", metadata={"path": str(file_path), "text": "hello"})

    response = agent.act(message)

    assert file_path.read_text() == "hello"
    assert agent.documents[file_path] == "hello"
    assert response.content == f"wrote {file_path}"


def test_writer_observe_updates_documents(tmp_path):
    """observe should record paths mentioned in messages."""
    agent = WriterAgent()
    file_path = tmp_path / "docs" / "extra.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("more text")
    message = Message(sender="manager", content=f"wrote {file_path}")

    agent.observe(message)

    assert agent.documents[file_path] == "more text"
