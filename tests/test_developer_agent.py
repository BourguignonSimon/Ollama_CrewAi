import pathlib
import sys

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agents.developer import DeveloperAgent


def test_developer_writes_code(tmp_path):
    developer = DeveloperAgent()
    target = tmp_path / "example.py"

    response = developer.act(path=target, code="print('hi')")

    assert target.read_text() == "print('hi')"
    assert response == f"wrote {target}"

    developer.observe(response)
    assert developer.last_written == target
