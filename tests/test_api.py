import pytest
from app.models import ServerState

@pytest.mark.asyncio
async def test_create_server(client):
    response = await client.post("/servers/", json={
        "hostname": "web-01",
        "ip_address": "192.168.1.10",
        "state": "active"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["hostname"] == "web-01"
    assert data["state"] == "active"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_duplicate_hostname(client):
    # Create first
    await client.post("/servers/", json={
        "hostname": "web-01",
        "ip_address": "192.168.1.10",
        "state": "active"
    })
    
    # Try duplicate
    response = await client.post("/servers/", json={
        "hostname": "web-01",
        "ip_address": "10.0.0.1",
        "state": "offline"
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_list_servers(client):
    await client.post("/servers/", json={"hostname": "s1", "ip_address": "1.1.1.1", "state": "active"})
    await client.post("/servers/", json={"hostname": "s2", "ip_address": "2.2.2.2", "state": "offline"})

    response = await client.get("/servers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

@pytest.mark.asyncio
async def test_get_server(client):
    r_create = await client.post("/servers/", json={"hostname": "s1", "ip_address": "1.1.1.1", "state": "active"})
    server_id = r_create.json()["id"]

    response = await client.get(f"/servers/{server_id}")
    assert response.status_code == 200
    assert response.json()["hostname"] == "s1"

@pytest.mark.asyncio
async def test_get_server_not_found(client):
    response = await client.get("/servers/999999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_server(client):
    r_create = await client.post("/servers/", json={"hostname": "s1", "ip_address": "1.1.1.1", "state": "active"})
    server_id = r_create.json()["id"]
    
    response = await client.put(f"/servers/{server_id}", json={"state": "retired"})
    assert response.status_code == 200
    assert response.json()["state"] == "retired"
    
    # Verify persistence
    r_get = await client.get(f"/servers/{server_id}")
    assert r_get.json()["state"] == "retired"

@pytest.mark.asyncio
async def test_delete_server(client):
    r_create = await client.post("/servers/", json={"hostname": "s1", "ip_address": "1.1.1.1", "state": "active"})
    server_id = r_create.json()["id"]

    response = await client.delete(f"/servers/{server_id}")
    assert response.status_code == 204
    
    # Verify gone
    r_get = await client.get(f"/servers/{server_id}")
    assert r_get.status_code == 404

@pytest.mark.asyncio
async def test_create_server_invalid_ip(client):
    response = await client.post("/servers/", json={
        "hostname": "test-invalid-ip",
        "ip_address": "invalid-ip-string",
        "state": "active"
    })
    assert response.status_code == 422
