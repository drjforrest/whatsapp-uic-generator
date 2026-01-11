"""
Structured logging configuration using structlog.
Provides consistent, queryable logs for production use.
"""
import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from app.config import settings


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to all log entries."""
    event_dict["app"] = settings.app_name
    event_dict["version"] = settings.app_version
    event_dict["environment"] = settings.environment
    return event_dict


def configure_logging() -> None:
    """Configure structured logging for the application."""

    # Determine if we should use JSON formatting
    use_json = settings.log_json or settings.is_production

    # Shared processors for all loggers
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
    ]

    if use_json:
        # JSON formatting for production
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Console formatting for development
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.processors.ExceptionPrettyPrinter(),
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )

    # Reduce noise from verbose libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name, typically __name__ of the calling module

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)
