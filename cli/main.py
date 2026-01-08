import typer
import requests
import json
import time
from typing import Optional
from enum import Enum
from functools import wraps

app = typer.Typer(help="Server Inventory CLI - Manage your server fleet")

API_URL = "http://localhost:8000/servers"

# Output format options
class OutputFormat(str, Enum):
    json = "json"
    table = "table"

class ServerState(str, Enum):
    active = "active"
    offline = "offline"
    retired = "retired"


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for exponential backoff retry on connection errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.ConnectionError as e:
                    last_exception = e
                    delay = base_delay * (2 ** attempt)
                    typer.echo(f"Connection failed, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})", err=True)
                    time.sleep(delay)
            typer.echo(f"Failed after {max_retries} attempts: {last_exception}", err=True)
            raise typer.Exit(1)
        return wrapper
    return decorator


def format_output(data, fmt: OutputFormat):
    """Format output based on user preference."""
    if fmt == OutputFormat.json:
        return json.dumps(data, indent=2, default=str)
    else:
        # Table format
        if isinstance(data, list):
            if not data:
                return "No servers found."
            headers = list(data[0].keys())
            lines = [" | ".join(headers)]
            lines.append("-" * len(lines[0]))
            for item in data:
                lines.append(" | ".join(str(item.get(h, "")) for h in headers))
            return "\n".join(lines)
        else:
            lines = [f"{k}: {v}" for k, v in data.items()]
            return "\n".join(lines)


@app.command()
@retry_with_backoff()
def create(
    hostname: str,
    ip_address: str,
    state: ServerState,
    format: OutputFormat = typer.Option(OutputFormat.table, "--format", "-f", help="Output format")
):
    """Create a new server."""
    payload = {
        "hostname": hostname,
        "ip_address": ip_address,
        "state": state.value
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code >= 400:
        typer.echo(f"Error: {response.text}", err=True)
        raise typer.Exit(1)
    typer.echo(format_output(response.json(), format))


@app.command("list")
@retry_with_backoff()
def list_servers(
    format: OutputFormat = typer.Option(OutputFormat.table, "--format", "-f", help="Output format"),
    state: Optional[str] = typer.Option(None, "--state", "-s", help="Filter by state"),
    hostname: Optional[str] = typer.Option(None, "--hostname", "-h", help="Filter by hostname (contains)")
):
    """List all servers with optional filtering."""
    params = {}
    if state:
        params["state"] = state
    if hostname:
        params["hostname_contains"] = hostname
    
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    typer.echo(format_output(response.json(), format))


@app.command()
@retry_with_backoff()
def get(
    server_id: int,
    format: OutputFormat = typer.Option(OutputFormat.table, "--format", "-f", help="Output format")
):
    """Get a specific server by ID."""
    response = requests.get(f"{API_URL}/{server_id}")
    if response.status_code == 404:
        typer.echo(f"Error: Server {server_id} not found", err=True)
        raise typer.Exit(1)
    response.raise_for_status()
    typer.echo(format_output(response.json(), format))


@app.command()
@retry_with_backoff()
def update(
    server_id: int,
    hostname: Optional[str] = typer.Option(None, "--hostname"),
    ip_address: Optional[str] = typer.Option(None, "--ip"),
    state: Optional[ServerState] = typer.Option(None, "--state"),
    format: OutputFormat = typer.Option(OutputFormat.table, "--format", "-f", help="Output format")
):
    """Update a server."""
    payload = {}
    if hostname:
        payload["hostname"] = hostname
    if ip_address:
        payload["ip_address"] = ip_address
    if state:
        payload["state"] = state.value
    
    if not payload:
        typer.echo("No updates specified. Use --hostname, --ip, or --state.", err=True)
        raise typer.Exit(1)

    response = requests.put(f"{API_URL}/{server_id}", json=payload)
    if response.status_code >= 400:
        typer.echo(f"Error: {response.text}", err=True)
        raise typer.Exit(1)
    typer.echo(format_output(response.json(), format))


@app.command()
@retry_with_backoff()
def delete(server_id: int):
    """Delete a server."""
    response = requests.delete(f"{API_URL}/{server_id}")
    if response.status_code == 404:
        typer.echo(f"Error: Server {server_id} not found", err=True)
        raise typer.Exit(1)
    response.raise_for_status()
    typer.echo(f"✓ Server {server_id} deleted successfully.")


if __name__ == "__main__":
    app()

