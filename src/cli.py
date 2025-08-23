"""Command-line interface for configuring and running agents.

This module reads a YAML or JSON configuration file describing the
available agents and creates a :class:`~agents.manager.Manager`
accordingly.  It also exposes a small CLI utility used via the
``ollama-crewai-agents`` entry point.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, cast

import os
import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

from agents.developer import DeveloperAgent
from agents.manager import Manager
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.tester import TesterAgent
from agents.writer import WriterAgent
from agents.message import Message
from supervisor.interface import display_progress, read_user_command
from contextlib import suppress

# Mapping from config keys to concrete agent classes
AGENT_TYPES = {
    "planner": PlannerAgent,
    "developer": DeveloperAgent,
    "writer": WriterAgent,
    "tester": TesterAgent,
    "researcher": ResearcherAgent,
}


class ConfigModel(BaseModel):
    """Schema for validating configuration files."""

    objective: str = ""
    agents: Dict[str, Dict[str, Any]]

    model_config = ConfigDict(extra="forbid")


def load_config(path: Path) -> Dict[str, Any]:
    """Load and validate a YAML or JSON configuration file.

    Parameters
    ----------
    path:
        Path to the configuration file.
    """

    text = path.read_text(encoding="utf-8")
    if path.suffix in {".yaml", ".yml"}:
        raw = cast(Dict[str, Any], yaml.safe_load(text))
    elif path.suffix == ".json":
        raw = cast(Dict[str, Any], json.loads(text))
    else:
        raise ValueError(f"Unsupported config format: {path.suffix}")

    try:
        cfg = ConfigModel.model_validate(raw)
    except ValidationError as exc:  # pragma: no cover - exercised in tests
        errors = "; ".join(
            f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in exc.errors()
        )
        raise ValueError(f"Invalid configuration: {errors}") from exc
    return cfg.model_dump()


def build_manager(config: Dict[str, Any]) -> Manager:
    """Create a :class:`Manager` based on ``config``.

    The configuration should contain an ``agents`` mapping where each key
    corresponds to an agent type listed in :data:`AGENT_TYPES`.
    """

    agents_cfg = config.get("agents", {})
    instances: Dict[str, Any] = {}
    for name, params in agents_cfg.items():
        cls = AGENT_TYPES.get(name)
        if cls is None:
            raise ValueError(f"Unknown agent type: {name}")
        if isinstance(params, dict):
            instances[name] = cls(**params)
        else:
            instances[name] = cls()
    return Manager(instances)


async def run_supervised(manager: Manager, objective: str) -> list:
    """Run ``manager`` with a simple supervisor interface."""

    async def supervisor_loop() -> None:
        while True:
            msg = await manager.bus.recv_from_supervisor()
            if msg.content == "plan":
                tasks = msg.metadata.get("tasks", []) if msg.metadata else []
                display_progress(tasks)
                cmd = await asyncio.to_thread(read_user_command) or "approve"
                manager.bus.send_to_supervisor(
                    Message(sender="supervisor", content=cmd)
                )
            elif msg.content == "progress":
                tasks = msg.metadata.get("tasks", []) if msg.metadata else []
                display_progress(tasks)

    ui_task = asyncio.create_task(supervisor_loop())
    try:
        return await manager.run(objective)
    finally:
        ui_task.cancel()
        with suppress(asyncio.CancelledError):
            await ui_task


def main() -> None:
    """Entry point for the ``ollama-crewai-agents`` script."""

    default_config = os.getenv("AGENTS_CONFIG", "config/agents.yaml")
    debug_default = os.getenv("AGENTS_DEBUG", "").lower() in {"1", "true", "yes"}

    parser = argparse.ArgumentParser(description="Run Ollama CrewAI agents")
    parser.add_argument(
        "-c",
        "--config",
        default=default_config,
        help="Path to YAML or JSON configuration file",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=debug_default,
        help="Enable debug logging",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    cfg = load_config(Path(args.config))
    manager = build_manager(cfg)
    objective = cfg.get("objective", "")

    tasks = asyncio.run(run_supervised(manager, objective))
    for task in tasks:
        logging.info("%s: %s", task.id, task.result or task.status.name)


if __name__ == "__main__":  # pragma: no cover - manual execution only
    main()
