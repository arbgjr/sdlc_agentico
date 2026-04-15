"""
Resilience primitives for SDLC Agêntico.

Provides retry with exponential backoff, timeout, and a minimal
circuit-breaker. Used to wrap any call that reaches outside the process
(MCP tools, HTTP clients, subprocess commands).

Why this exists: cross-process calls fail. Silent retries hide the
failure; no retries amplify transient errors into incidents. The
resilience decorators make the policy explicit and per-callsite.

No external dependencies — stdlib only so this file is importable from
anywhere in the framework without installing packages.

Constitution reference: Principle VII (observability/quality of
delivery) — every wrapped call emits structured outcome events via
``sdlc_logging`` when available.
"""
from __future__ import annotations

import functools
import logging
import random
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

try:  # pragma: no cover — optional dep
    from sdlc_logging import get_logger  # type: ignore

    logger = get_logger("resilience")
except Exception:  # pragma: no cover
    logger = logging.getLogger("sdlc.resilience")
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.WARNING)


T = TypeVar("T")


class RetryableError(Exception):
    """Raise this to force a retry without subclassing the caller's error type."""


class CircuitOpenError(RuntimeError):
    """Raised when a call is refused because the circuit breaker is open."""


# ---------------------------------------------------------------------------
# Retry with exponential backoff + jitter
# ---------------------------------------------------------------------------


def with_retry(
    max_attempts: int = 3,
    base_delay_seconds: float = 0.5,
    max_delay_seconds: float = 10.0,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
    give_up_on: tuple[type[BaseException], ...] = (),
    jitter: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator: retry the call on ``retry_on`` up to ``max_attempts`` times.

    Exponential backoff ``base * 2**(attempt-1)`` capped at ``max_delay``,
    optional full jitter to prevent thundering herds.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exc: BaseException | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except give_up_on:
                    raise
                except retry_on as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        logger.warning(
                            "retry.exhausted",
                            extra={
                                "function": func.__qualname__,
                                "attempts": attempt,
                                "error_type": type(exc).__name__,
                            },
                        )
                        raise
                    delay = min(
                        max_delay_seconds,
                        base_delay_seconds * (2 ** (attempt - 1)),
                    )
                    if jitter:
                        delay = random.uniform(0, delay)  # noqa: S311 — jitter, not crypto
                    logger.info(
                        "retry.attempt",
                        extra={
                            "function": func.__qualname__,
                            "attempt": attempt,
                            "next_delay_s": round(delay, 3),
                            "error_type": type(exc).__name__,
                        },
                    )
                    time.sleep(delay)
            # Unreachable, appeases type checker
            raise last_exc if last_exc else RuntimeError("unreachable")

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Timeout (signal-based on main thread, threading.Timer fallback)
# ---------------------------------------------------------------------------


def with_timeout(seconds: float) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator: raise TimeoutError if ``func`` runs longer than ``seconds``.

    Uses a daemon thread to poll — portable across platforms (Windows
    does not support SIGALRM). Do not use for functions that must run
    in the main thread exclusively.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            result: list[Any] = []
            error: list[BaseException] = []

            def target() -> None:
                try:
                    result.append(func(*args, **kwargs))
                except BaseException as exc:  # noqa: BLE001
                    error.append(exc)

            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            thread.join(timeout=seconds)
            if thread.is_alive():
                logger.warning(
                    "timeout.exceeded",
                    extra={"function": func.__qualname__, "timeout_s": seconds},
                )
                raise TimeoutError(
                    f"{func.__qualname__} exceeded {seconds}s timeout"
                )
            if error:
                raise error[0]
            return result[0]

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------


@dataclass
class _CircuitState:
    name: str
    failure_threshold: float  # 0..1
    window_size: int
    cooldown_seconds: float
    outcomes: list[bool] = field(default_factory=list)  # True=success, False=failure
    opened_at: float | None = None
    lock: threading.Lock = field(default_factory=threading.Lock)

    def record(self, success: bool) -> None:
        with self.lock:
            self.outcomes.append(success)
            if len(self.outcomes) > self.window_size:
                self.outcomes = self.outcomes[-self.window_size :]

    def should_trip(self) -> bool:
        if len(self.outcomes) < self.window_size:
            return False
        failures = sum(1 for ok in self.outcomes if not ok)
        rate = failures / self.window_size
        return rate >= self.failure_threshold

    def is_open(self, now: float) -> bool:
        if self.opened_at is None:
            return False
        if now - self.opened_at >= self.cooldown_seconds:
            # Half-open: allow one probe
            with self.lock:
                self.opened_at = None
                self.outcomes = []
            logger.info("circuit.half_open", extra={"breaker_name": self.name})
            return False
        return True

    def open(self, now: float) -> None:
        with self.lock:
            self.opened_at = now
        logger.warning(
            "circuit.opened",
            extra={
                "breaker_name": self.name,
                "cooldown_s": self.cooldown_seconds,
                "window_failures": sum(1 for ok in self.outcomes if not ok),
            },
        )


_BREAKERS: dict[str, _CircuitState] = {}
_BREAKERS_LOCK = threading.Lock()


def with_circuit_breaker(
    name: str,
    failure_threshold: float = 0.5,
    window_size: int = 10,
    cooldown_seconds: float = 30.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator: refuse calls while the breaker is open (recent failure rate).

    ``name`` identifies the breaker, so all decorated callsites with the
    same name share state. Pick distinct names per external dependency.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        with _BREAKERS_LOCK:
            if name not in _BREAKERS:
                _BREAKERS[name] = _CircuitState(
                    name=name,
                    failure_threshold=failure_threshold,
                    window_size=window_size,
                    cooldown_seconds=cooldown_seconds,
                )
        state = _BREAKERS[name]

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            now = time.time()
            if state.is_open(now):
                raise CircuitOpenError(
                    f"circuit '{name}' is open — call refused"
                )
            try:
                outcome = func(*args, **kwargs)
            except BaseException:
                state.record(False)
                if state.should_trip():
                    state.open(time.time())
                raise
            state.record(True)
            return outcome

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Composite helpers
# ---------------------------------------------------------------------------


def resilient(
    *,
    name: str,
    timeout_s: float = 15.0,
    max_attempts: int = 3,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
    give_up_on: tuple[type[BaseException], ...] = (CircuitOpenError,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """One-stop decorator: timeout + retry + circuit breaker.

    Order of application (outer -> inner): circuit breaker, retry, timeout.
    The timeout is innermost so it bounds each retry attempt independently.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        wrapped = with_timeout(timeout_s)(func)
        wrapped = with_retry(
            max_attempts=max_attempts,
            retry_on=retry_on,
            give_up_on=give_up_on,
        )(wrapped)
        wrapped = with_circuit_breaker(name=name)(wrapped)
        return wrapped

    return decorator


__all__ = [
    "CircuitOpenError",
    "RetryableError",
    "resilient",
    "with_circuit_breaker",
    "with_retry",
    "with_timeout",
]
