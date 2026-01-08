import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager

from app.config import settings

# Connection pool - reuses connections for better performance
pool: AsyncConnectionPool | None = None

async def init_pool():
    """Initialize the connection pool. Call on app startup."""
    global pool
    pool = AsyncConnectionPool(
        conninfo=settings.DATABASE_URL,
        min_size=2,
        max_size=10,
        kwargs={"row_factory": dict_row},
    )
    await pool.open()

async def close_pool():
    """Close the connection pool. Call on app shutdown."""
    global pool
    if pool:
        await pool.close()

class Database:
    """Legacy class for backward compatibility."""
    def __init__(self):
        self.conn_str = settings.DATABASE_URL

    @asynccontextmanager
    async def get_connection(self):
        conn = await psycopg.AsyncConnection.connect(self.conn_str, row_factory=dict_row)
        try:
            yield conn
        finally:
            await conn.close()

db = Database()

async def get_db_connection():
    """Dependency that provides a pooled database connection."""
    global pool
    if pool:
        async with pool.connection() as conn:
            yield conn
    else:
        # Fallback for tests or when pool isn't initialized
        async with db.get_connection() as conn:
            yield conn

