from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime

class ReadyResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Liveness probe - is the service running?"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow()
    )

@router.get("/ready", response_model=ReadyResponse)
async def readiness_check():
    """Readiness probe - is the service ready to accept traffic?"""
    from app.database import db
    
    try:
        async with db.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return ReadyResponse(
        status="ready" if db_status == "connected" else "not_ready",
        database=db_status,
        timestamp=datetime.utcnow()
    )
