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

import yaml

from agents.developer import DeveloperAgent
from agents.manager import Manager
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.tester import TesterAgent
from agents.writer import WriterAgent

# Mapping from config keys to concrete agent classes
AGENT_TYPES = {
    "planner": PlannerAgent,
    "developer": DeveloperAgent,
    "writer": WriterAgent,
    "tester": TesterAgent,
    "researcher": ResearcherAgent,
}


def load_config(path: Path) -> Dict[str, Any]:
    """Load a YAML or JSON configuration file.

    Parameters
    ----------
    path:
        Path to the configuration file.
    """

    text = path.read_text(encoding="utf-8")
    if path.suffix in {".yaml", ".yml"}:
        return cast(Dict[str, Any], yaml.safe_load(text))
    if path.suffix == ".json":
        return cast(Dict[str, Any], json.loads(text))
    raise ValueError(f"Unsupported config format: {path.suffix}")


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


def main() -> None:
    """Entry point for the ``ollama-crewai-agents`` script."""

    parser = argparse.ArgumentParser(description="Run Ollama CrewAI agents")
    parser.add_argument(
        "-c",
        "--config",
        default="config/agents.yaml",
        help="Path to YAML or JSON configuration file",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    cfg = load_config(Path(args.config))
    manager = build_manager(cfg)
    objective = cfg.get("objective", "")

    tasks = asyncio.run(manager.run(objective))
    for task in tasks:
        logging.info("%s: %s", task.id, task.result or task.status.name)


if __name__ == "__main__":  # pragma: no cover - manual execution only
    main()
