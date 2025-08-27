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
import os
import sys
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import ValidationError
from langchain_ollama import OllamaLLM

from agents.developer import DeveloperAgent
from agents.manager import Manager
from agents.message import Message
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.tester import TesterAgent
from agents.writer import WriterAgent
from config.schema import ConfigModel
from core import policies
from core.storage import Storage
from supervisor import interface

# Mapping from config keys to concrete agent classes
AGENT_TYPES = {
    "planner": PlannerAgent,
    "developer": DeveloperAgent,
    "writer": WriterAgent,
    "tester": TesterAgent,
    "researcher": ResearcherAgent,
}


def build_manager(config: ConfigModel | Dict[str, Any]) -> Manager:
    """Create a :class:`Manager` based on ``config``.

    The configuration should contain an ``agents`` mapping where each key
    corresponds to an agent type listed in :data:`AGENT_TYPES`.
    """

    if not isinstance(config, ConfigModel):
        config = ConfigModel.model_validate(config)

    agents_cfg = config.agents
    instances: Dict[str, Any] = {}
    for name, params in agents_cfg.items():
        cls = AGENT_TYPES.get(name)
        if cls is None:
            raise ValueError(f"Unknown agent type: {name}")
        llm_cfg = params.llm
        llm = OllamaLLM(
            model=llm_cfg.model,
            base_url=llm_cfg.base_url,
            temperature=llm_cfg.temperature,
        )
        instances[name] = cls(
            role=params.role,
            goal=params.goal,
            backstory=params.backstory,
            llm=llm,
        )
    if config.policies.allowed_commands is not None:
        policies.ALLOWED_COMMANDS = set(config.policies.allowed_commands)
    if config.policies.network_access is not None:
        policies.NETWORK_ACCESS = config.policies.network_access
    storage = Storage(config.storage.path) if config.storage else None
    return Manager(instances, storage=storage)


def load_config(path: Path) -> ConfigModel:
    """Load and validate a YAML or JSON configuration file.

    Parameters
    ----------
    path:
        Path to the configuration file.
    """

    text = path.read_text(encoding="utf-8")
    if path.suffix in {".yaml", ".yml"}:
        raw = yaml.safe_load(text)  # type: ignore[assignment]
    elif path.suffix == ".json":
        raw = json.loads(text)
    else:
        raise ValueError(f"Unsupported config format: {path.suffix}")

    try:
        return ConfigModel.model_validate(raw)
    except ValidationError as exc:
        errors = "; ".join(
            f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in exc.errors()
        )
        raise ValueError(f"Invalid configuration at {path}: {errors}") from exc


async def run_supervised(manager: Manager, objective: str) -> list:
    """Run ``manager`` with a simple supervisor interface."""

    async def supervisor_loop() -> None:
        while True:
            msg = await manager.bus.recv_from_supervisor()
            if msg.content == "plan":
                tasks = msg.metadata.get("tasks", []) if msg.metadata else []
                interface.display_progress(tasks)
                cmd = await asyncio.to_thread(interface.read_user_command) or "approve"
                manager.bus.send_to_supervisor(
                    Message(sender="supervisor", content=cmd)
                )
                await asyncio.sleep(0)
            elif msg.content == "progress":
                tasks = msg.metadata.get("tasks", []) if msg.metadata else []
                interface.display_progress(tasks)
            else:
                manager.bus.dispatch("supervisor", msg)
                await asyncio.sleep(0)

    ui_task = asyncio.create_task(supervisor_loop())
    try:
        return await manager.run(objective)
    finally:
        ui_task.cancel()
        with suppress(asyncio.CancelledError):
            await ui_task


async def run_basic(manager: Manager, objective: str) -> list:
    """Run ``manager`` without interactive supervision."""

    async def auto_approve() -> None:
        await manager.bus.recv_from_supervisor()
        manager.bus.send_to_supervisor(Message(sender="supervisor", content="approve"))

    ui_task = asyncio.create_task(auto_approve())
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
    try:
        cfg = load_config(Path(args.config))
    except ValueError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1) from exc
    manager = build_manager(cfg)
    objective = cfg.objective

    if cfg.supervision.enabled:
        tasks = asyncio.run(run_supervised(manager, objective))
    else:
        tasks = asyncio.run(run_basic(manager, objective))
    for task in tasks:
        logging.info("%s: %s", task.id, task.result or task.status.name)


if __name__ == "__main__":  # pragma: no cover - manual execution only
    main()
