# Inventory Management System API & CLI

## Overview
This project provides a REST API and a CLI for tracking server inventory. It uses FastAPI, PostgreSQL, and Typer.

## Requirements
- Docker & Docker Compose
- Python 3.10+ (for local CLI usage, optional)

## Running the Stack
To start the API and Database:
```bash
docker-compose up --build

# Or using Podman
podman compose up --build

```
The API will be available at `http://localhost:8000`.
Documentation (Swagger UI) is available at `http://localhost:8000/docs`.

## Running Tests
Tests are written using `pytest`. You can run them locally if you have valid python environment:

1. Install dependencies:
   ```bash
   pip install .[test]
   ```
2. Run tests:
   ```bash
   pytest
   ```

## CLI Usage
The CLI is a python script in `cli/main.py`.

1. Ensure specific dependencies are installed or use the same environment:
   ```bash
   pip install typer requests
   ```
2. Run commands:
   ```bash
   # Create a server
   python cli/main.py create web-01 192.168.1.5 active

   # List servers
   python cli/main.py list

   # Get a server
   python cli/main.py get 1

   # Update a server
   python cli/main.py update 1 --state offline

   # Delete a server
   python cli/main.py delete 1
   ```

## API Specification

### Endpoints

#### POST /servers
Create a new server.
- **Body**:
    ```json
    {
        "hostname": "string",
        "ip_address": "string (IPv4)",
        "state": "active|offline|retired"
    }
    ```
- **Response**: 201 Created

#### GET /servers
List all servers.
- **Response**: 200 OK (List of servers)

#### GET /servers/{id}
Get a specific server.
- **Response**: 200 OK or 404 Not Found

#### PUT /servers/{id}
Update a server.
- **Body** (all fields optional):
    ```json
    {
        "hostname": "string",
        "ip_address": "string",
        "state": "string"
    }
    ```
- **Response**: 200 OK

#### DELETE /servers/{id}
Delete a server.
- **Response**: 204 No Content
