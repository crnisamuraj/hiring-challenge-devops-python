from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import router as servers_router
from app.health import router as health_router
from app.metrics import router as metrics_router
from app.database import init_pool, close_pool
from app.logging import setup_logging
from app.tracing import setup_tracing
from app.middleware import RequestIDMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    setup_logging(json_logs=False)  # Set to True in production
    await init_pool()
    yield
    await close_pool()

app = FastAPI(
    title="Server Inventory API",
    description="CRUD API for managing server inventory",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(RequestIDMiddleware)

# Setup observability
setup_tracing(app)

# API versioning - mount servers under /v1
app.include_router(servers_router, prefix="/v1")

# Keep backward compatibility with non-versioned endpoints
app.include_router(servers_router)

# Utility routers (no versioning needed)
app.include_router(health_router)
app.include_router(metrics_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Server Inventory API", "version": "1.0.0"}



