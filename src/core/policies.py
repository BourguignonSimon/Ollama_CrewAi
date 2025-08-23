"""Basic policy rules for agent actions.

Defines a simple whitelist based command policy and a network
restriction check used by the :class:`~agents.manager.Manager`.
"""
from __future__ import annotations

from typing import Iterable

# Default whitelist of allowed command keywords.  These cover the
# commands used in the test suite and represent typical safe actions.
ALLOWED_COMMANDS: set[str] = {
    "alpha",
    "beta",
    "gamma",
    "delta",
    "task",
    "hello",
}

# Whether network access is permitted.  When set to ``False`` any task
# containing an obvious URL will be rejected.
NETWORK_ACCESS: bool = False

def is_command_allowed(description: str, *, allowed: Iterable[str] | None = None) -> bool:
    """Return ``True`` if ``description`` starts with an allowed command.

    Parameters
    ----------
    description:
        Full textual description of the task.
    allowed:
        Optional custom iterable of allowed commands.  If ``None`` the global
        :data:`ALLOWED_COMMANDS` is used.
    """
    words = description.strip().split()
    if not words:
        return True
    whitelist = set(allowed) if allowed is not None else ALLOWED_COMMANDS
    return words[0].lower() in whitelist

def is_network_allowed(description: str, *, network_allowed: bool | None = None) -> bool:
    """Check network policy for ``description``.

    If ``network_allowed`` is ``False`` any occurrence of ``http://`` or
    ``https://`` causes the check to fail.
    """
    allowed = NETWORK_ACCESS if network_allowed is None else network_allowed
    if allowed:
        return True
    lowered = description.lower()
    return "http://" not in lowered and "https://" not in lowered

def check_policy(description: str) -> bool:
    """Validate ``description`` against command and network policies."""
    return is_command_allowed(description) and is_network_allowed(description)
