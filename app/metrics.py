"""Prometheus metrics configuration."""
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response
import time
from functools import wraps

router = APIRouter(tags=["metrics"])

# Define metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

SERVERS_CREATED = Counter(
    "servers_created_total",
    "Total number of servers created"
)

SERVERS_DELETED = Counter(
    "servers_deleted_total",
    "Total number of servers deleted"
)

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record metrics for a request."""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
