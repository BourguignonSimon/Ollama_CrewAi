import pathlib
import sys

import pytest

# Ensure src directory on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from config.schema import load_config, ConfigModel


def test_valid_config(tmp_path):
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text(
        "objective: 'alpha.'\n"
        "agents:\n  planner: {}\n"
        "policies:\n  allowed_commands: [alpha]\n  network_access: true\n"
        "storage:\n  path: state.json\n"
        "supervision:\n  enabled: true\n"
    )
    cfg = load_config(cfg_file)
    assert isinstance(cfg, ConfigModel)
    assert cfg.policies.allowed_commands == ["alpha"]
    assert cfg.storage.path == "state.json"
    assert cfg.supervision.enabled is True


def test_invalid_agent_config(tmp_path):
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text("agents:\n  planner: 'oops'\n")
    with pytest.raises(ValueError) as excinfo:
        load_config(cfg_file)
    assert "agents.planner" in str(excinfo.value)
