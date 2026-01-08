from fastapi import APIRouter, Depends, HTTPException, status, Header, Response
from psycopg import AsyncConnection
from psycopg.errors import UniqueViolation
from typing import List, Optional

from app.database import get_db_connection
from app.models import Server, ServerCreate, ServerUpdate
from app.etag import generate_etag, etag_matches, etag_none_match

router = APIRouter(prefix="/servers", tags=["servers"])


@router.post("/", response_model=Server, status_code=status.HTTP_201_CREATED)
async def create_server(
    response: Response,
    server: ServerCreate,
    conn: AsyncConnection = Depends(get_db_connection)
):
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
            
            # Add ETag header to response
            etag = generate_etag(new_server)
            response.headers["ETag"] = f'"{etag}"'
            
            return new_server
    except UniqueViolation:
        await conn.rollback()
        raise HTTPException(status_code=400, detail="Server with this hostname already exists")


@router.get("/", response_model=List[Server])
async def list_servers(
    limit: int = 100,
    offset: int = 0,
    state: Optional[str] = None,
    hostname_contains: Optional[str] = None,
    conn: AsyncConnection = Depends(get_db_connection)
):
    """List servers with optional filtering.
    
    Args:
        limit: Maximum number of results (default 100)
        offset: Pagination offset (default 0)
        state: Filter by server state (active, offline, retired)
        hostname_contains: Filter servers whose hostname contains this string
    """
    # Build dynamic WHERE clause
    conditions = []
    params = []
    
    if state:
        conditions.append("state = %s")
        params.append(state)
    
    if hostname_contains:
        conditions.append("hostname ILIKE %s")
        params.append(f"%{hostname_contains}%")
    
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)
    
    query = f"""
        SELECT id, hostname, ip_address, state, created_at 
        FROM servers 
        {where_clause}
        ORDER BY id 
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    
    async with conn.cursor() as cur:
        await cur.execute(query, params)
        servers = await cur.fetchall()
        return servers


@router.get("/{server_id}", response_model=Server)
async def get_server(
    server_id: int,
    response: Response,
    conn: AsyncConnection = Depends(get_db_connection),
    if_none_match: Optional[str] = Header(None)
):
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, hostname, ip_address, state, created_at FROM servers WHERE id = %s",
            (server_id,)
        )
        server = await cur.fetchone()
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")
        
        # Generate ETag
        etag = generate_etag(server)
        response.headers["ETag"] = f'"{etag}"'
        
        # Check If-None-Match for conditional GET (304 Not Modified)
        if etag_none_match(etag, if_none_match):
            return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers={"ETag": f'"{etag}"'})
        
        return server


@router.put("/{server_id}", response_model=Server)
async def update_server(
    server_id: int,
    server_update: ServerUpdate,
    response: Response,
    conn: AsyncConnection = Depends(get_db_connection),
    if_match: Optional[str] = Header(None)
):
    # Build query dynamically based on set fields
    update_data = server_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # If If-Match is provided, verify the ETag before updating
    if if_match:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, hostname, ip_address, state, created_at FROM servers WHERE id = %s",
                (server_id,)
            )
            current = await cur.fetchone()
            if not current:
                raise HTTPException(status_code=404, detail="Server not found")
            
            current_etag = generate_etag(current)
            if not etag_matches(current_etag, if_match):
                raise HTTPException(
                    status_code=status.HTTP_412_PRECONDITION_FAILED,
                    detail="Resource has been modified. Refresh and retry."
                )

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
            
            # Add new ETag to response
            etag = generate_etag(updated_server)
            response.headers["ETag"] = f'"{etag}"'
            
            return updated_server
    except UniqueViolation:
        await conn.rollback()
        raise HTTPException(status_code=400, detail="Server with this hostname already exists")


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: int,
    conn: AsyncConnection = Depends(get_db_connection),
    if_match: Optional[str] = Header(None)
):
    # If If-Match is provided, verify the ETag before deleting
    if if_match:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, hostname, ip_address, state, created_at FROM servers WHERE id = %s",
                (server_id,)
            )
            current = await cur.fetchone()
            if not current:
                raise HTTPException(status_code=404, detail="Server not found")
            
            current_etag = generate_etag(current)
            if not etag_matches(current_etag, if_match):
                raise HTTPException(
                    status_code=status.HTTP_412_PRECONDITION_FAILED,
                    detail="Resource has been modified. Refresh and retry."
                )

    async with conn.cursor() as cur:
        await cur.execute("DELETE FROM servers WHERE id = %s RETURNING id", (server_id,))
        deleted = await cur.fetchone()
        if not deleted:
            raise HTTPException(status_code=404, detail="Server not found")
        await conn.commit()

