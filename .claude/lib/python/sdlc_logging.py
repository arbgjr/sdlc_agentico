#!/usr/bin/env python3
"""
SDLC Agentico Logging Module

Provides structured JSON logging with Loki integration and OpenTelemetry tracing.
Default level: DEBUG (verbose mode for SDLC development).

Usage:
    from sdlc_logging import get_logger, with_context

    logger = get_logger(__name__)
    logger.info("Processing started", extra={"phase": 3, "skill": "graph-navigator"})

    with with_context(correlation_id="abc-123", phase=5):
        logger.debug("Detailed operation")
"""

import logging
import logging.handlers
import json
import os
import sys
import uuid
import threading
import time
from datetime import datetime, timezone
from typing import Any, Optional, Dict, Callable
from contextvars import ContextVar
from contextlib import contextmanager
from functools import wraps

# ============================================================================
# Configuration
# ============================================================================

# Environment variables with defaults
SDLC_LOG_LEVEL = os.environ.get("SDLC_LOG_LEVEL", "DEBUG").upper()
SDLC_LOKI_URL = os.environ.get("SDLC_LOKI_URL", "http://localhost:3100")
SDLC_LOKI_ENABLED = os.environ.get("SDLC_LOKI_ENABLED", "true").lower() == "true"
SDLC_JSON_LOGS = os.environ.get("SDLC_JSON_LOGS", "true").lower() == "true"
SDLC_PROJECT_ROOT = os.environ.get("SDLC_PROJECT_ROOT", os.getcwd())
SDLC_ENV = os.environ.get("SDLC_ENV", "development")

# Log level mapping
LOG_LEVELS = {
    "VERBOSE": logging.DEBUG,  # Alias for DEBUG
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# ============================================================================
# Context Management
# ============================================================================

# Thread-local context for correlation IDs and metadata
_context: ContextVar[Dict[str, Any]] = ContextVar("sdlc_context", default={})


def get_context() -> Dict[str, Any]:
    """Get current logging context."""
    return _context.get().copy()


def set_context(**kwargs) -> None:
    """Set context values for current execution."""
    ctx = _context.get().copy()
    ctx.update(kwargs)
    _context.set(ctx)


def clear_context() -> None:
    """Clear all context values."""
    _context.set({})


@contextmanager
def with_context(**kwargs):
    """
    Context manager for temporary context values.

    Usage:
        with with_context(correlation_id="abc-123", phase=5):
            logger.info("This log has correlation_id and phase")
    """
    old_ctx = _context.get().copy()
    new_ctx = old_ctx.copy()
    new_ctx.update(kwargs)
    _context.set(new_ctx)
    try:
        yield
    finally:
        _context.set(old_ctx)


def generate_correlation_id() -> str:
    """Generate a unique correlation ID."""
    return str(uuid.uuid4())[:8]


def get_or_create_correlation_id() -> str:
    """Get existing correlation ID from context or create new one."""
    ctx = _context.get()
    if "correlation_id" not in ctx:
        set_context(correlation_id=generate_correlation_id())
    return _context.get()["correlation_id"]


# ============================================================================
# JSON Formatter
# ============================================================================

class SDLCJsonFormatter(logging.Formatter):
    """
    JSON log formatter for structured logging.

    Output format compatible with Loki/Grafana:
    {
        "timestamp": "2025-01-15T10:30:00.123456Z",
        "level": "INFO",
        "logger": "decay_calculator",
        "message": "Processing nodes",
        "correlation_id": "abc12345",
        "skill": "decay-scoring",
        "phase": 6,
        "script": "decay_calculator.py",
        "extra": {...}
    }
    """

    RESERVED_ATTRS = {
        "name", "msg", "args", "created", "filename", "funcName",
        "levelname", "levelno", "lineno", "module", "msecs",
        "pathname", "process", "processName", "relativeCreated",
        "stack_info", "exc_info", "exc_text", "thread", "threadName",
        "taskName", "message"
    }

    def format(self, record: logging.LogRecord) -> str:
        # Base log structure
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add context from ContextVar
        ctx = get_context()
        if ctx:
            log_entry.update(ctx)

        # Add script/module info
        log_entry["script"] = os.path.basename(record.pathname)
        log_entry["function"] = record.funcName
        log_entry["line"] = record.lineno

        # Extract extra fields from record
        extra = {}
        for key, value in record.__dict__.items():
            if key not in self.RESERVED_ATTRS and not key.startswith("_"):
                try:
                    json.dumps(value)  # Test serializability
                    extra[key] = value
                except (TypeError, ValueError):
                    extra[key] = str(value)

        if extra:
            log_entry["extra"] = extra

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }

        # Add trace ID if available
        try:
            from .sdlc_tracing import get_current_trace_id
            trace_id = get_current_trace_id()
            if trace_id:
                log_entry["trace_id"] = trace_id
        except ImportError:
            pass

        return json.dumps(log_entry, default=str, ensure_ascii=False)


class SDLCConsoleFormatter(logging.Formatter):
    """
    Human-readable console formatter with colors.
    Used when SDLC_JSON_LOGS=false.
    """

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        ctx = get_context()
        correlation_id = ctx.get("correlation_id", "-")[:8]

        # Format: [LEVEL   ] [corr_id ] logger: message
        prefix = f"{color}[{record.levelname:8}]{self.RESET}"
        prefix += f" [{correlation_id:8}]"
        prefix += f" {record.name}:"

        message = record.getMessage()

        # Add extra fields inline
        extras = []
        for key, value in record.__dict__.items():
            if key not in SDLCJsonFormatter.RESERVED_ATTRS and not key.startswith("_"):
                extras.append(f"{key}={value}")

        if extras:
            message += f" ({', '.join(extras)})"

        formatted = f"{prefix} {message}"

        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)

        return formatted


# ============================================================================
# Loki Handler
# ============================================================================

class LokiHandler(logging.Handler):
    """
    Log handler that sends logs to Loki via HTTP Push API.

    Batches logs and sends them periodically or when buffer is full.
    """

    def __init__(
        self,
        url: str = SDLC_LOKI_URL,
        labels: Optional[Dict[str, str]] = None,
        batch_size: int = 100,
        flush_interval: float = 5.0,
    ):
        super().__init__()
        self.url = url.rstrip("/") + "/loki/api/v1/push"
        self.default_labels = labels or {}
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self._buffer: list = []
        self._buffer_lock = threading.Lock()
        self._timer: Optional[threading.Timer] = None
        self._closed = False

        # Start flush timer
        self._start_timer()

    def _start_timer(self):
        """Start the periodic flush timer."""
        if self._closed:
            return
        self._timer = threading.Timer(self.flush_interval, self._timer_flush)
        self._timer.daemon = True
        self._timer.start()

    def _timer_flush(self):
        """Flush triggered by timer."""
        self.flush()
        self._start_timer()

    def emit(self, record: logging.LogRecord):
        """Add log record to buffer."""
        if self._closed:
            return

        try:
            # Format as JSON
            msg = self.format(record)

            # Build labels from context and record
            ctx = get_context()
            labels = self.default_labels.copy()
            labels["level"] = record.levelname.lower()
            labels["logger"] = record.name

            # Add context labels
            for key in ["skill", "phase", "agent", "correlation_id"]:
                if key in ctx:
                    labels[key] = str(ctx[key])

            # Loki timestamp in nanoseconds
            timestamp = str(int(record.created * 1e9))

            with self._buffer_lock:
                self._buffer.append({
                    "labels": labels,
                    "timestamp": timestamp,
                    "line": msg,
                })

                if len(self._buffer) >= self.batch_size:
                    self._flush_buffer()

        except Exception:
            self.handleError(record)

    def _flush_buffer(self):
        """Flush buffer to Loki (must be called with lock held)."""
        if not self._buffer:
            return

        # Group by labels
        streams: Dict[str, dict] = {}
        for entry in self._buffer:
            label_key = json.dumps(entry["labels"], sort_keys=True)
            if label_key not in streams:
                streams[label_key] = {
                    "stream": entry["labels"],
                    "values": []
                }
            streams[label_key]["values"].append([entry["timestamp"], entry["line"]])

        payload = {"streams": list(streams.values())}
        self._buffer.clear()

        # Send to Loki (fire and forget to avoid blocking)
        try:
            import urllib.request
            import urllib.error

            req = urllib.request.Request(
                self.url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=5) as response:
                pass  # Success

        except Exception as e:
            # Log to stderr as fallback (don't raise to avoid infinite loop)
            sys.stderr.write(f"[SDLC] Failed to send logs to Loki: {e}\n")

    def flush(self):
        """Flush buffered logs to Loki."""
        with self._buffer_lock:
            self._flush_buffer()

    def close(self):
        """Close handler and flush remaining logs."""
        self._closed = True
        if self._timer:
            self._timer.cancel()
        self.flush()
        super().close()


# ============================================================================
# Logger Factory
# ============================================================================

_loggers: Dict[str, logging.Logger] = {}
_initialized = False


def _initialize_logging():
    """Initialize root logger configuration."""
    global _initialized
    if _initialized:
        return

    # Get root logger
    root = logging.getLogger()
    root.setLevel(LOG_LEVELS.get(SDLC_LOG_LEVEL, logging.DEBUG))

    # Remove existing handlers
    root.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(LOG_LEVELS.get(SDLC_LOG_LEVEL, logging.DEBUG))

    if SDLC_JSON_LOGS:
        console_handler.setFormatter(SDLCJsonFormatter())
    else:
        console_handler.setFormatter(SDLCConsoleFormatter())

    root.addHandler(console_handler)

    # Loki handler (if enabled)
    if SDLC_LOKI_ENABLED:
        try:
            loki_handler = LokiHandler(
                url=SDLC_LOKI_URL,
                labels={
                    "app": "sdlc-agentico",
                    "env": SDLC_ENV,
                }
            )
            loki_handler.setLevel(LOG_LEVELS.get(SDLC_LOG_LEVEL, logging.DEBUG))
            loki_handler.setFormatter(SDLCJsonFormatter())
            root.addHandler(loki_handler)
        except Exception as e:
            sys.stderr.write(f"[SDLC] Failed to initialize Loki handler: {e}\n")

    _initialized = True


def get_logger(
    name: str,
    skill: Optional[str] = None,
    phase: Optional[int] = None,
    **extra_context
) -> logging.Logger:
    """
    Get or create a logger with SDLC context.

    Args:
        name: Logger name (typically __name__ or script name)
        skill: SDLC skill name (e.g., "decay-scoring", "graph-navigator")
        phase: SDLC phase number (0-8)
        **extra_context: Additional context to attach to all logs

    Returns:
        Configured logger instance

    Example:
        logger = get_logger(__name__, skill="decay-scoring", phase=6)
        logger.info("Processing started", extra={"node_count": 42})
    """
    _initialize_logging()

    # Normalize name
    if name == "__main__":
        name = os.path.basename(sys.argv[0]).replace(".py", "")

    # Get or create logger
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)

    logger = _loggers[name]

    # Set context if provided
    if skill or phase is not None or extra_context:
        ctx = {}
        if skill:
            ctx["skill"] = skill
        if phase is not None:
            ctx["phase"] = phase
        ctx.update(extra_context)
        set_context(**ctx)

    return logger


# ============================================================================
# Decorators
# ============================================================================

def log_function(logger: Optional[logging.Logger] = None, level: int = logging.DEBUG):
    """
    Decorator to log function entry, exit, and exceptions.

    Usage:
        @log_function()
        def my_function(arg1, arg2):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or get_logger(func.__module__)
            func_name = func.__name__

            _logger.log(level, f"Entering {func_name}", extra={
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys()),
            })

            try:
                result = func(*args, **kwargs)
                _logger.log(level, f"Exiting {func_name}", extra={
                    "result_type": type(result).__name__,
                })
                return result

            except Exception as e:
                _logger.exception(f"Exception in {func_name}", extra={
                    "exception_type": type(e).__name__,
                })
                raise

        return wrapper
    return decorator


@contextmanager
def log_operation(operation_name: str, logger: Optional[logging.Logger] = None):
    """
    Context manager for logging operations with timing.

    Usage:
        with log_operation("process_nodes", logger):
            # ... operation code ...
    """
    _logger = logger or get_logger("sdlc")
    start_time = time.time()

    _logger.info(f"Starting: {operation_name}")

    try:
        yield
        duration = time.time() - start_time
        _logger.info(f"Completed: {operation_name}", extra={
            "duration_ms": round(duration * 1000, 2),
            "status": "success",
        })

    except Exception as e:
        duration = time.time() - start_time
        _logger.error(f"Failed: {operation_name}", extra={
            "duration_ms": round(duration * 1000, 2),
            "status": "error",
            "error_type": type(e).__name__,
        })
        raise


# ============================================================================
# Convenience Functions
# ============================================================================

def log_phase_transition(from_phase: int, to_phase: int, gate_status: str, **extra):
    """Log SDLC phase transition."""
    logger = get_logger("phase_transition")
    logger.info(
        f"Phase transition: {from_phase} -> {to_phase}",
        extra={
            "from_phase": from_phase,
            "to_phase": to_phase,
            "gate_status": gate_status,
            **extra
        }
    )


def log_gate_evaluation(gate_name: str, passed: bool, details: Dict[str, Any]):
    """Log quality gate evaluation."""
    logger = get_logger("gate_evaluation")
    level = logging.INFO if passed else logging.WARNING
    logger.log(
        level,
        f"Gate '{gate_name}': {'PASSED' if passed else 'FAILED'}",
        extra={
            "gate_name": gate_name,
            "gate_passed": passed,
            "gate_details": details,
        }
    )


def log_security_event(event_type: str, severity: str, details: Dict[str, Any]):
    """Log security-related events."""
    logger = get_logger("security")
    levels = {
        "critical": logging.CRITICAL,
        "high": logging.ERROR,
        "medium": logging.WARNING,
        "low": logging.INFO,
    }
    level = levels.get(severity.lower(), logging.WARNING)
    logger.log(
        level,
        f"Security event: {event_type}",
        extra={
            "security_event_type": event_type,
            "security_severity": severity,
            "security_details": details,
        }
    )


# ============================================================================
# Module-level initialization
# ============================================================================

# Auto-initialize when module is imported
_initialize_logging()
