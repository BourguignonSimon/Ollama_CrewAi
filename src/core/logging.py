from __future__ import annotations

import logging

LOG_FORMAT = "%(levelname)s|%(agent)s|%(task)s|%(message)s"


class TaskLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that merges call-time ``extra`` with default context."""

    def process(self, msg: str, kwargs: dict) -> tuple[str, dict]:
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


def get_logger(agent: str, level: int = logging.INFO) -> TaskLoggerAdapter:
    """Return a structured logger for ``agent``.

    The logger emits entries containing the log level, agent name and
    task identifier. Additional task information can be supplied at log
    call time via the ``extra`` argument.
    """
    logger = logging.getLogger(agent)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
    logger.setLevel(level)
    return TaskLoggerAdapter(logger, {"agent": agent})
