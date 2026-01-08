import typer
import requests
import json
from typing import Optional
from enum import Enum

app = typer.Typer()

API_URL = "http://localhost:8000/servers"

class ServerState(str, Enum):
    active = "active"
    offline = "offline"
    retired = "retired"

@app.command()
def create(hostname: str, ip_address: str, state: ServerState):
    """Create a new server."""
    payload = {
        "hostname": hostname,
        "ip_address": ip_address,
        "state": state.value
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        typer.echo(json.dumps(response.json(), indent=2))
    except requests.exceptions.HTTPError as e:
         typer.echo(f"Error: {e.response.text}", err=True)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)

@app.command("list")
def list_servers():
    """List all servers."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        typer.echo(json.dumps(response.json(), indent=2))
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)

@app.command()
def get(server_id: int):
    """Get a specific server by ID."""
    try:
        response = requests.get(f"{API_URL}/{server_id}")
        response.raise_for_status()
        typer.echo(json.dumps(response.json(), indent=2))
    except requests.exceptions.HTTPError as e:
        typer.echo(f"Error: {e.response.text}", err=True)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)

@app.command()
def update(server_id: int, hostname: Optional[str] = None, ip_address: Optional[str] = None, state: Optional[ServerState] = None):
    """Update a server."""
    payload = {}
    if hostname:
        payload["hostname"] = hostname
    if ip_address:
        payload["ip_address"] = ip_address
    if state:
        payload["state"] = state.value
    
    if not payload:
        typer.echo("No updates specific.")
        return

    try:
        response = requests.put(f"{API_URL}/{server_id}", json=payload)
        response.raise_for_status()
        typer.echo(json.dumps(response.json(), indent=2))
    except requests.exceptions.HTTPError as e:
        typer.echo(f"Error: {e.response.text}", err=True)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)

@app.command()
def delete(server_id: int):
    """Delete a server."""
    try:
        response = requests.delete(f"{API_URL}/{server_id}")
        response.raise_for_status()
        typer.echo(f"Server {server_id} deleted successfully.")
    except requests.exceptions.HTTPError as e:
        typer.echo(f"Error: {e.response.text}", err=True)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    app()
