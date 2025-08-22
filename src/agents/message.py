"""Messaging constructs for agent communication."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(slots=True)
class Message:
    """Represents a message exchanged between agents.

    Parameters
    ----------
    sender:
        Identifier of the agent sending the message.
    content:
        The textual content of the message.
    metadata:
        Optional dictionary carrying arbitrary metadata associated with the
        message (timestamps, routing information, etc.).
    """

    sender: str
    content: str
    metadata: Optional[Dict[str, Any]] = field(default=None)
