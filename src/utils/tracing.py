"""OpenTelemetry tracing setup. No-ops cleanly when disabled."""
from __future__ import annotations

from typing import Any

from src.utils.config_parser import get_env, get_env_bool
from src.utils.logger import get_logger

log = get_logger(__name__)
_tracer: Any = None


def init_tracing() -> None:
    global _tracer
    if not get_env_bool("OTEL_ENABLED", False):
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": get_env("OTEL_SERVICE_NAME", "llm-forge")})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=get_env("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"), insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer("llm-forge")
        log.info("otel_initialized")
    except Exception as e:  # noqa: BLE001
        log.warning("otel_init_failed", error=str(e))


def get_tracer() -> Any:
    return _tracer


def instrument_fastapi(app: Any) -> None:
    if not get_env_bool("OTEL_ENABLED", False):
        return
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
    except Exception as e:  # noqa: BLE001
        log.warning("otel_fastapi_instrument_failed", error=str(e))
