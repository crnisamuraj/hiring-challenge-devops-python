import os
import psycopg
from psycopg.rows import dict_row
from contextlib import asynccontextmanager

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5432/inventory")

class Database:
    def __init__(self):
        self.conn_str = DATABASE_URL

    @asynccontextmanager
    async def get_connection(self):
        conn = await psycopg.AsyncConnection.connect(self.conn_str, row_factory=dict_row)
        try:
            yield conn
        finally:
            await conn.close()

db = Database()

async def get_db_connection():
    async with db.get_connection() as conn:
        yield conn
