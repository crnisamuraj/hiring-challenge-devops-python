# Server Inventory API & CLI

## Overview
REST API and CLI for tracking server inventory. Built with FastAPI, PostgreSQL (raw SQL), and Typer.

## Quick Start

```bash
# Start with Docker/Podman
podman compose up -d --build

# Run tests
podman compose exec api pytest -v

# View API docs
open http://localhost:8000/docs
```

## Makefile Commands

```bash
make help          # Show all commands
make podman-up     # Start the stack
make podman-test   # Run tests in container
make lint          # Run linter
make format        # Format code
```

---

## API Endpoints

### CRUD Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/servers` | Create a server |
| GET | `/servers` | List servers (with filtering) |
| GET | `/servers/{id}` | Get a server |
| PUT | `/servers/{id}` | Update a server |
| DELETE | `/servers/{id}` | Delete a server |

### Filtering & Pagination

```bash
GET /servers?limit=10&offset=0              # Pagination
GET /servers?state=active                   # Filter by state
GET /servers?hostname_contains=web          # Search hostname
GET /servers?state=active&hostname_contains=web  # Combined
```

### ETag Concurrency Control

All responses include an `ETag` header for optimistic concurrency:

```bash
# Conditional GET (returns 304 if unchanged)
curl -H "If-None-Match: \"abc123\"" http://localhost:8000/servers/1

# Conditional PUT (returns 412 if stale)
curl -X PUT -H "If-Match: \"abc123\"" -d '{"state":"offline"}' http://localhost:8000/servers/1
```

### Health & Observability

| Endpoint | Description |
|----------|-------------|
| `/health` | Liveness probe |
| `/ready` | Readiness probe (checks DB) |
| `/metrics` | Prometheus metrics |

### API Versioning

All endpoints are available at both `/servers` and `/v1/servers`.

---

## CLI Usage

```bash
# Basic commands
python cli/main.py create web-01 192.168.1.5 active
python cli/main.py list
python cli/main.py get 1
python cli/main.py update 1 --state offline
python cli/main.py delete 1

# Output formats
python cli/main.py list --format json    # JSON output
python cli/main.py list --format table   # Table output (default)

# Filtering
python cli/main.py list --state active
python cli/main.py list --hostname web
```

### CLI Features
- **Retry with backoff** - Auto-retries on connection errors
- **Format options** - `--format json` or `--format table`
- **Filtering** - `--state` and `--hostname` flags

---

## Request Tracing

All responses include `X-Request-ID` header for distributed tracing.
Send your own `X-Request-ID` header and it will be echoed back.

---

## Development

```bash
# Install dev dependencies
pip install -e ".[test,dev]"

# Run pre-commit hooks
pre-commit install
pre-commit run --all-files

# Run Alembic migrations
alembic upgrade head
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://admin:password@db:5432/inventory` | Database connection |
| `POSTGRES_USER` | `admin` | DB username |
| `POSTGRES_PASSWORD` | `password` | DB password |
| `POSTGRES_DB` | `inventory` | DB name |
| `OTEL_CONSOLE_EXPORT` | `false` | Enable trace console output |
