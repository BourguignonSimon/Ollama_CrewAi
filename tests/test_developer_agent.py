import pathlib
import sys

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents import Message
from agents.developer import DeveloperAgent


def test_developer_writes_code(tmp_path):
    developer = DeveloperAgent()
    target = tmp_path / "example.py"
    msg = Message(
        sender="tester",
        content="write",
        metadata={"path": target, "code": "print('hi')"},
    )

    response = developer.act(msg)

    assert target.read_text() == "print('hi')"
    assert response.content == f"wrote {target}"

    developer.observe(response)
    assert developer.last_written == target
    assert "coding" in developer.capabilities
