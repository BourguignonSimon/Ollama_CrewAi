import pathlib
import sys

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Message
from agents.writer import WriterAgent


def test_writer_act_writes_file_and_updates_documents(tmp_path):
    agent = WriterAgent()
    file_path = tmp_path / "docs" / "output.txt"
    message = Message(sender="tester", content="", metadata={"path": str(file_path), "text": "hello"})

    response = agent.act(message)

    assert file_path.read_text() == "hello"
    assert agent.documents == [file_path]
    assert response.content == f"wrote {file_path}"


def test_writer_observe_adds_document(tmp_path):
    agent = WriterAgent()
    file_path = tmp_path / "docs" / "extra.txt"
    message = Message(sender="manager", content=f"wrote {file_path}")

    agent.observe(message)

    assert agent.documents == [file_path]
