from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation
from typing import List

from app.database import get_db_connection
from app.models import Server, ServerCreate, ServerUpdate

router = APIRouter(prefix="/servers", tags=["servers"])

@router.post("/", response_model=Server, status_code=status.HTTP_201_CREATED)
async def create_server(server: ServerCreate, conn: AsyncConnection = Depends(get_db_connection)):
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO servers (hostname, ip_address, state)
                VALUES (%s, %s, %s)
                RETURNING id, hostname, ip_address, state, created_at
                """,
                (server.hostname, str(server.ip_address), server.state.value)
            )
            new_server = await cur.fetchone()
            await conn.commit()
            return new_server
    except UniqueViolation:
        await conn.rollback()
        raise HTTPException(status_code=400, detail="Server with this hostname already exists")

@router.get("/", response_model=List[Server])
async def list_servers(conn: AsyncConnection = Depends(get_db_connection)):
    async with conn.cursor() as cur:
        await cur.execute("SELECT id, hostname, ip_address, state, created_at FROM servers")
        servers = await cur.fetchall()
        return servers

@router.get("/{server_id}", response_model=Server)
async def get_server(server_id: int, conn: AsyncConnection = Depends(get_db_connection)):
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, hostname, ip_address, state, created_at FROM servers WHERE id = %s",
            (server_id,)
        )
        server = await cur.fetchone()
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")
        return server

@router.put("/{server_id}", response_model=Server)
async def update_server(server_id: int, server_update: ServerUpdate, conn: AsyncConnection = Depends(get_db_connection)):
    # Build query dynamically based on set fields
    update_data = server_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clauses = []
    values = []
    for key, value in update_data.items():
        if key == 'ip_address':
            value = str(value)
        elif key == 'state':
            value = value.value
        
        set_clauses.append(f"{key} = %s")
        values.append(value)
    
    values.append(server_id)
    
    query = f"""
        UPDATE servers
        SET {", ".join(set_clauses)}
        WHERE id = %s
        RETURNING id, hostname, ip_address, state, created_at
    """

    try:
        async with conn.cursor() as cur:
            await cur.execute(query, values)
            updated_server = await cur.fetchone()
            if not updated_server:
                raise HTTPException(status_code=404, detail="Server not found")
            await conn.commit()
            return updated_server
    except UniqueViolation:
        await conn.rollback()
        raise HTTPException(status_code=400, detail="Server with this hostname already exists")

@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(server_id: int, conn: AsyncConnection = Depends(get_db_connection)):
    async with conn.cursor() as cur:
        await cur.execute("DELETE FROM servers WHERE id = %s RETURNING id", (server_id,))
        deleted = await cur.fetchone()
        if not deleted:
            raise HTTPException(status_code=404, detail="Server not found")
        await conn.commit()
