"""
SDLC Agentico Logging Library

Provides structured logging with Loki integration and optional OpenTelemetry tracing.

Usage:
    from sdlc_logging import get_logger, with_context

    logger = get_logger(__name__, skill="my-skill", phase=5)
    logger.info("Operation started", extra={"key": "value"})
"""

from .sdlc_logging import (
    get_logger,
    get_context,
    set_context,
    clear_context,
    with_context,
    generate_correlation_id,
    get_or_create_correlation_id,
    log_function,
    log_operation,
    log_phase_transition,
    log_gate_evaluation,
    log_security_event,
)

__all__ = [
    "get_logger",
    "get_context",
    "set_context",
    "clear_context",
    "with_context",
    "generate_correlation_id",
    "get_or_create_correlation_id",
    "log_function",
    "log_operation",
    "log_phase_transition",
    "log_gate_evaluation",
    "log_security_event",
]

__version__ = "1.7.0"
