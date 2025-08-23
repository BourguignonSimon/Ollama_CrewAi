import asyncio
import pathlib
import sys

# Ensure src directory is on the path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import cli  # type: ignore
import pytest


def test_cli_load_and_run(tmp_path):
    cfg_file = tmp_path / "agents.yaml"
    cfg_file.write_text(
        "objective: 'alpha. beta.'\n"
        "agents:\n"
        "  planner: {}\n"
        "  developer: {}\n"
    )
    cfg = cli.load_config(cfg_file)
    manager = cli.build_manager(cfg)
    tasks = asyncio.run(manager.run(cfg["objective"]))
    assert len(tasks) == 2


def test_cli_invalid_config(tmp_path):
    cfg_file = tmp_path / "agents.yaml"
    cfg_file.write_text(
        "objective: 'gamma'\n"
        "agents:\n"
        "  planner: 'not-a-dict'\n"
    )
    with pytest.raises(ValueError) as excinfo:
        cli.load_config(cfg_file)
    assert "agents.planner" in str(excinfo.value)
