#!/usr/bin/env python3
"""
SDLC Agentico Tracing Module

Provides OpenTelemetry-based distributed tracing with Tempo integration.

Usage:
    from sdlc_tracing import get_tracer, trace_function

    tracer = get_tracer(__name__)

    with tracer.start_as_current_span("operation_name") as span:
        span.set_attribute("phase", 5)
        # ... operation code ...
"""

import os
import sys
from typing import Optional, Dict, Any, Callable
from functools import wraps
from contextlib import contextmanager

# Environment configuration
SDLC_TEMPO_URL = os.environ.get("SDLC_TEMPO_URL", "http://localhost:4318")
SDLC_TRACE_ENABLED = os.environ.get("SDLC_TRACE_ENABLED", "true").lower() == "true"
SDLC_SERVICE_NAME = os.environ.get("SDLC_SERVICE_NAME", "sdlc-agentico")
SDLC_ENV = os.environ.get("SDLC_ENV", "development")
SDLC_VERSION = os.environ.get("SDLC_VERSION", "1.7.0")

# Try to import OpenTelemetry (optional dependency)
_otel_available = False
_tracer = None
_trace = None
_Status = None
_StatusCode = None

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

    _otel_available = True
    _trace = trace
    _Status = Status
    _StatusCode = StatusCode
except ImportError:
    pass


def _initialize_tracing():
    """Initialize OpenTelemetry tracing."""
    global _tracer

    if not SDLC_TRACE_ENABLED or not _otel_available:
        return

    if _tracer is not None:
        return

    try:
        # Create resource with service info
        resource = Resource.create({
            "service.name": SDLC_SERVICE_NAME,
            "service.version": SDLC_VERSION,
            "deployment.environment": SDLC_ENV,
        })

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Configure OTLP exporter to Tempo
        exporter = OTLPSpanExporter(
            endpoint=f"{SDLC_TEMPO_URL}/v1/traces",
        )

        # Add batch processor
        provider.add_span_processor(BatchSpanProcessor(exporter))

        # Set as global tracer provider
        _trace.set_tracer_provider(provider)

        _tracer = _trace.get_tracer(__name__)

    except Exception as e:
        sys.stderr.write(f"[SDLC] Failed to initialize tracing: {e}\n")


class NoOpSpan:
    """No-op span for when tracing is disabled."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def set_attribute(self, key: str, value: Any):
        pass

    def set_status(self, status):
        pass

    def record_exception(self, exception: Exception):
        pass

    def add_event(self, name: str, attributes: Optional[Dict] = None):
        pass


class NoOpTracer:
    """No-op tracer for when OpenTelemetry is not available."""

    @contextmanager
    def start_as_current_span(self, name: str, **kwargs):
        yield NoOpSpan()

    def start_span(self, name: str, **kwargs):
        return NoOpSpan()


def get_tracer(name: str = __name__):
    """
    Get a tracer instance.

    Returns a no-op tracer if OpenTelemetry is not available or tracing is disabled.

    Args:
        name: Tracer name (typically __name__)

    Returns:
        Tracer instance
    """
    if not SDLC_TRACE_ENABLED or not _otel_available:
        return NoOpTracer()

    _initialize_tracing()

    if _tracer is None:
        return NoOpTracer()

    return _trace.get_tracer(name)


def trace_function(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
):
    """
    Decorator to trace function execution.

    Usage:
        @trace_function(attributes={"skill": "graph-navigator"})
        def my_function():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer(func.__module__)
            span_name = name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add function info
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                try:
                    result = func(*args, **kwargs)
                    if _otel_available and _Status and _StatusCode:
                        span.set_status(_Status(_StatusCode.OK))
                    return result

                except Exception as e:
                    if _otel_available and _Status and _StatusCode:
                        span.set_status(_Status(_StatusCode.ERROR, str(e)))
                        span.record_exception(e)
                    raise

        return wrapper
    return decorator


def get_current_trace_id() -> Optional[str]:
    """Get the current trace ID, if available."""
    if not _otel_available or not SDLC_TRACE_ENABLED or not _trace:
        return None

    try:
        current_span = _trace.get_current_span()
        if current_span:
            span_context = current_span.get_span_context()
            if span_context and span_context.trace_id:
                return format(span_context.trace_id, '032x')
    except Exception:
        pass

    return None


def get_current_span_id() -> Optional[str]:
    """Get the current span ID, if available."""
    if not _otel_available or not SDLC_TRACE_ENABLED or not _trace:
        return None

    try:
        current_span = _trace.get_current_span()
        if current_span:
            span_context = current_span.get_span_context()
            if span_context and span_context.span_id:
                return format(span_context.span_id, '016x')
    except Exception:
        pass

    return None


def inject_trace_context(carrier: Dict[str, str]) -> Dict[str, str]:
    """
    Inject trace context into a carrier dict for propagation.

    Useful for passing trace context to subprocesses or HTTP requests.

    Args:
        carrier: Dictionary to inject context into

    Returns:
        The carrier with trace context injected
    """
    if not _otel_available or not SDLC_TRACE_ENABLED:
        return carrier

    try:
        from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
        propagator = TraceContextTextMapPropagator()
        propagator.inject(carrier)
    except Exception:
        pass

    return carrier


def extract_trace_context(carrier: Dict[str, str]):
    """
    Extract trace context from a carrier dict.

    Useful for receiving trace context from parent processes.

    Args:
        carrier: Dictionary containing trace context

    Returns:
        Extracted context or None
    """
    if not _otel_available or not SDLC_TRACE_ENABLED:
        return None

    try:
        from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
        propagator = TraceContextTextMapPropagator()
        return propagator.extract(carrier)
    except Exception:
        pass

    return None


@contextmanager
def trace_operation(
    operation_name: str,
    attributes: Optional[Dict[str, Any]] = None
):
    """
    Context manager for tracing an operation.

    Usage:
        with trace_operation("process_data", {"batch_size": 100}):
            # ... operation code ...
    """
    tracer = get_tracer("sdlc_operations")

    with tracer.start_as_current_span(operation_name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        try:
            yield span
            if _otel_available and _Status and _StatusCode:
                span.set_status(_Status(_StatusCode.OK))
        except Exception as e:
            if _otel_available and _Status and _StatusCode:
                span.set_status(_Status(_StatusCode.ERROR, str(e)))
                span.record_exception(e)
            raise
