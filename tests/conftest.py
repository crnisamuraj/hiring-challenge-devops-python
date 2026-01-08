import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_db_connection, db
from app.config import settings
import psycopg

# Use a different DB for testing if possible, or just the same one for this simple task
# In a real world, we'd spin up a test container or create a test_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_pool():
    # Ensure tables exist
    # In a real app, we would run alembic migrations here
    # For this task, we will just execute init.sql content
    conn_str = settings.DATABASE_URL
    async with await psycopg.AsyncConnection.connect(conn_str, autocommit=True) as conn:
        async with conn.cursor() as cur:
             # Very simple teardown/rebuild for fresh state
             await cur.execute("DROP TABLE IF EXISTS servers CASCADE")
             await cur.execute("DROP TYPE IF EXISTS server_state CASCADE")
             
             # Re-create (Read init.sql would be better, but hardcoding for simplicity of this artifact)
             await cur.execute("""
                DO $$ BEGIN
                    CREATE TYPE server_state AS ENUM ('active', 'offline', 'retired');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
                
                CREATE TABLE IF NOT EXISTS servers (
                    id SERIAL PRIMARY KEY,
                    hostname VARCHAR(255) NOT NULL UNIQUE,
                    ip_address INET,
                    state server_state NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
             """)
    yield

@pytest.fixture
async def override_get_db(db_pool):
    # We want a fresh transaction for each test that rolls back
    # But for simplicity with psycopg3 async, we can just TRUNCATE or similar.
    # Proper transactional tests are complex to setup without TestContainers or specific libs.
    # Let's go with TRUNCATE for simplicity.
    async with db.get_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("TRUNCATE TABLE servers RESTART IDENTITY")
            await conn.commit()
    
    # Return the actual dependency
    async for conn in get_db_connection():
        yield conn

@pytest.fixture
async def client(override_get_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
