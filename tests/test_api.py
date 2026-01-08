import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.database import get_db_connection
from app.models import ServerState

@pytest.fixture
def mock_db_cursor():
    cursor = AsyncMock()
    # Mock context manager behavior for cursor
    cursor.__aenter__.return_value = cursor
    cursor.__aexit__.return_value = None
    return cursor

@pytest.fixture
def mock_db_connection(mock_db_cursor):
    connection = AsyncMock()
    connection.cursor = MagicMock(return_value=mock_db_cursor)
    connection.commit = AsyncMock()
    connection.rollback = AsyncMock()
    return connection

@pytest.fixture
def override_get_db(mock_db_connection):
    async def _override():
        yield mock_db_connection
    return _override

from httpx import AsyncClient, ASGITransport

@pytest.fixture
def client(override_get_db):
    app.dependency_overrides[get_db_connection] = override_get_db
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")

@pytest.mark.asyncio
async def test_create_server(client, mock_db_cursor):
    mock_db_cursor.fetchone.return_value = {
        "id": 1,
        "hostname": "web-01",
        "ip_address": "192.168.1.10",
        "state": "active",
        "created_at": "2023-01-01T00:00:00"
    }

    response = await client.post("/servers/", json={
        "hostname": "web-01",
        "ip_address": "192.168.1.10",
        "state": "active"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["hostname"] == "web-01"
    assert data["state"] == "active"

@pytest.mark.asyncio
async def test_list_servers(client, mock_db_cursor):
    mock_db_cursor.fetchall.return_value = [
        {
            "id": 1,
            "hostname": "web-01",
            "ip_address": "192.168.1.10",
            "state": "active",
            "created_at": "2023-01-01T00:00:00"
        }
    ]

    response = await client.get("/servers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["hostname"] == "web-01"

@pytest.mark.asyncio
async def test_get_server_not_found(client, mock_db_cursor):
    mock_db_cursor.fetchone.return_value = None
    response = await client.get("/servers/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_server_invalid_ip(client):
    response = await client.post("/servers/", json={
        "hostname": "test",
        "ip_address": "invalid-ip",
        "state": "active"
    })
    assert response.status_code == 422
