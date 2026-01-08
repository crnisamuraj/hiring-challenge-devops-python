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


# ETag Tests
@pytest.mark.asyncio
async def test_etag_returned_on_create(client):
    """Test that ETag is returned when creating a server."""
    response = await client.post("/servers/", json={
        "hostname": "etag-test",
        "ip_address": "10.0.0.1",
        "state": "active"
    })
    assert response.status_code == 201
    assert "etag" in response.headers


@pytest.mark.asyncio
async def test_etag_returned_on_get(client):
    """Test that ETag is returned when getting a server."""
    r_create = await client.post("/servers/", json={
        "hostname": "etag-get-test",
        "ip_address": "10.0.0.2",
        "state": "active"
    })
    server_id = r_create.json()["id"]
    
    response = await client.get(f"/servers/{server_id}")
    assert response.status_code == 200
    assert "etag" in response.headers


@pytest.mark.asyncio
async def test_if_none_match_returns_304(client):
    """Test conditional GET with If-None-Match returns 304 Not Modified."""
    r_create = await client.post("/servers/", json={
        "hostname": "conditional-get-test",
        "ip_address": "10.0.0.3",
        "state": "active"
    })
    server_id = r_create.json()["id"]
    
    # First GET to get ETag
    r_get = await client.get(f"/servers/{server_id}")
    etag = r_get.headers["etag"]
    
    # Conditional GET with same ETag should return 304
    response = await client.get(f"/servers/{server_id}", headers={"If-None-Match": etag})
    assert response.status_code == 304


@pytest.mark.asyncio
async def test_if_match_update_succeeds(client):
    """Test update with correct If-Match header succeeds."""
    r_create = await client.post("/servers/", json={
        "hostname": "if-match-test",
        "ip_address": "10.0.0.4",
        "state": "active"
    })
    server_id = r_create.json()["id"]
    etag = r_create.headers["etag"]
    
    response = await client.put(
        f"/servers/{server_id}",
        json={"state": "offline"},
        headers={"If-Match": etag}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_if_match_update_fails_with_stale_etag(client):
    """Test update with stale If-Match header returns 412 Precondition Failed."""
    r_create = await client.post("/servers/", json={
        "hostname": "stale-etag-test",
        "ip_address": "10.0.0.5",
        "state": "active"
    })
    server_id = r_create.json()["id"]
    old_etag = r_create.headers["etag"]
    
    # Update to change the ETag
    await client.put(f"/servers/{server_id}", json={"state": "offline"})
    
    # Try to update with old ETag
    response = await client.put(
        f"/servers/{server_id}",
        json={"state": "retired"},
        headers={"If-Match": old_etag}
    )
    assert response.status_code == 412


# Filtering Tests
@pytest.mark.asyncio
async def test_filter_by_state(client):
    """Test filtering servers by state."""
    await client.post("/servers/", json={"hostname": "filter-active", "ip_address": "10.1.1.1", "state": "active"})
    await client.post("/servers/", json={"hostname": "filter-offline", "ip_address": "10.1.1.2", "state": "offline"})
    
    response = await client.get("/servers/?state=active")
    assert response.status_code == 200
    data = response.json()
    assert all(s["state"] == "active" for s in data)


@pytest.mark.asyncio
async def test_filter_by_hostname_contains(client):
    """Test filtering servers by hostname pattern."""
    await client.post("/servers/", json={"hostname": "web-prod-01", "ip_address": "10.2.1.1", "state": "active"})
    await client.post("/servers/", json={"hostname": "db-prod-01", "ip_address": "10.2.1.2", "state": "active"})
    
    response = await client.get("/servers/?hostname_contains=web")
    assert response.status_code == 200
    data = response.json()
    assert all("web" in s["hostname"] for s in data)


# Request ID Test
@pytest.mark.asyncio
async def test_request_id_header(client):
    """Test that X-Request-ID header is returned in responses."""
    response = await client.get("/servers/")
    assert "x-request-id" in response.headers


