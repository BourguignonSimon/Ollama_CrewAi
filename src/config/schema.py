from __future__ import annotations

"""Pydantic models for validating application configuration."""

from pathlib import Path
from typing import Any, Dict, List

import json
import yaml
from pydantic import BaseModel, ConfigDict, ValidationError


class PoliciesConfig(BaseModel):
    """Configuration for command and network policies."""

    allowed_commands: List[str] | None = None
    network_access: bool | None = None

    model_config = ConfigDict(extra="forbid")


class StorageConfig(BaseModel):
    """Configuration of persistence storage."""

    path: str

    model_config = ConfigDict(extra="forbid")


class SupervisionConfig(BaseModel):
    """Options for supervisor interaction."""

    enabled: bool = True

    model_config = ConfigDict(extra="forbid")


class ConfigModel(BaseModel):
    """Top-level application configuration."""

    objective: str = ""
    agents: Dict[str, Dict[str, Any]]
    policies: PoliciesConfig = PoliciesConfig()
    storage: StorageConfig | None = None
    supervision: SupervisionConfig = SupervisionConfig()

    model_config = ConfigDict(extra="forbid")


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
    except ValidationError as exc:  # pragma: no cover - exercised in tests
        errors = "; ".join(
            f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in exc.errors()
        )
        raise ValueError(f"Invalid configuration: {errors}") from exc
