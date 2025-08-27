"""Command-line interface for configuring and running a CrewAI crew.

This module reads a YAML or JSON configuration file describing the
available agents, builds a set of :class:`crewai.Agent` instances and
their corresponding :class:`crewai.Task`s and finally executes them using
``Crew.kickoff``.  It also exposes a small CLI utility used via the
``ollama-crewai-agents`` entry point.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml
from crewai import Crew, Process, Task
from pydantic import ValidationError

from agents.developer import DeveloperAgent
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.tester import TesterAgent
from agents.writer import WriterAgent
from config.schema import ConfigModel
from core import policies

# Mapping from config keys to concrete agent classes
AGENT_TYPES = {
    "planner": PlannerAgent,
    "developer": DeveloperAgent,
    "writer": WriterAgent,
    "tester": TesterAgent,
    "researcher": ResearcherAgent,
}


def build_crew(
    config: ConfigModel | Dict[str, Any],
    *,
    process: Process = Process.sequential,
) -> Crew:
    """Create a :class:`Crew` based on ``config``."""

    if not isinstance(config, ConfigModel):
        config = ConfigModel.model_validate(config)

    agents_cfg = config.agents
    instances: Dict[str, Any] = {}
    for name, params in agents_cfg.items():
        cls = AGENT_TYPES.get(name)
        if cls is None:
            raise ValueError(f"Unknown agent type: {name}")
        if isinstance(params, dict):
            instances[name] = cls(**params)
        else:
            instances[name] = cls()

    if config.policies.allowed_commands is not None:
        policies.ALLOWED_COMMANDS = set(config.policies.allowed_commands)
    if config.policies.network_access is not None:
        policies.NETWORK_ACCESS = config.policies.network_access

    tasks: List[Task] = []

    planner_task: Task | None = None
    if "planner" in instances:
        planner_task = Task(
            description=f"Plan the steps to achieve the objective: {config.objective}",
            agent=instances["planner"],
            expected_output="A numbered list of tasks to complete",
        )
        tasks.append(planner_task)

    research_task: Task | None = None
    if "researcher" in instances:
        research_task = Task(
            description="Collect any external information required.",
            agent=instances["researcher"],
            expected_output="Summary of research findings",
            context=[planner_task] if planner_task else None,
        )
        tasks.append(research_task)

    develop_task: Task | None = None
    if "developer" in instances:
        ctx = [t for t in [planner_task, research_task] if t]
        develop_task = Task(
            description="Implement the planned solution.",
            agent=instances["developer"],
            expected_output="Source code files",
            context=ctx or None,
        )
        tasks.append(develop_task)

    if "tester" in instances:
        tasks.append(
            Task(
                description="Test the implementation and report results.",
                agent=instances["tester"],
                expected_output="Test reports",
                context=[develop_task] if develop_task else None,
            )
        )

    if "writer" in instances:
        tasks.append(
            Task(
                description="Write documentation for the project.",
                agent=instances["writer"],
                expected_output="Documentation text",
                context=[develop_task] if develop_task else None,
            )
        )

    return Crew(agents=list(instances.values()), tasks=tasks, process=process)


def load_config(path: Path) -> ConfigModel:
    """Load and validate a YAML or JSON configuration file."""

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

    crew = build_crew(cfg, process=Process.sequential)
    crew.kickoff(inputs={"objective": cfg.objective})

    for task in crew.tasks:
        logging.info("%s", getattr(task, "output", None))


if __name__ == "__main__":  # pragma: no cover - manual execution only
    main()

