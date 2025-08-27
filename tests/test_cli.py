import asyncio
import pathlib
import sys

# Ensure src directory is on the path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import cli  # type: ignore
import pytest
from agents.message import Message


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

    async def orchestrate() -> list:
        run_task = asyncio.create_task(manager.run(cfg.objective))
        plan = await asyncio.wait_for(manager.bus.recv_from_supervisor(), timeout=1)
        assert plan.content == "plan"
        manager.bus.send_to_supervisor(Message(sender="supervisor", content="approve"))
        return await run_task

    tasks = asyncio.run(orchestrate())
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
    message = str(excinfo.value)
    assert str(cfg_file) in message
    assert "agents.planner" in message


def test_cli_main_invalid_config(tmp_path, monkeypatch, capsys):
    cfg_file = tmp_path / "agents.yaml"
    cfg_file.write_text(
        "objective: 'delta'\n"
        "agents:\n"
        "  planner: 'nope'\n"
    )
    monkeypatch.setenv("AGENTS_DEBUG", "0")
    monkeypatch.setenv("AGENTS_CONFIG", str(cfg_file))
    monkeypatch.setattr(sys, "argv", ["prog", "-c", str(cfg_file)])
    with pytest.raises(SystemExit):
        cli.main()
    err = capsys.readouterr().err
    assert str(cfg_file) in err
    assert "agents.planner" in err
