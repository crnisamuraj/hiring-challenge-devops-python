"""OpenTelemetry tracing configuration."""
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

_provider = None

def setup_tracing(app, service_name: str = "server-inventory-api"):
    """Configure OpenTelemetry tracing for the application."""
    global _provider
    
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })
    
    _provider = TracerProvider(resource=resource)
    
    # Only add console exporter if explicitly enabled (avoids I/O errors)
    # In production, use OTLP exporter instead
    if os.getenv("OTEL_CONSOLE_EXPORT", "").lower() == "true":
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        _provider.add_span_processor(processor)
    
    trace.set_tracer_provider(_provider)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

def shutdown_tracing():
    """Shutdown tracing provider gracefully."""
    global _provider
    if _provider:
        _provider.shutdown()

def get_tracer(name: str = __name__):
    """Get a tracer instance for manual instrumentation."""
    return trace.get_tracer(name)

