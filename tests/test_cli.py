from typer.testing import CliRunner
from cli.main import app
from unittest.mock import patch, MagicMock

runner = CliRunner()

def test_list_servers():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "hostname": "test"}]
    
    with patch("requests.get", return_value=mock_response) as mock_get:
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "test" in result.stdout
        mock_get.assert_called_once()

def test_create_server():
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 1, "hostname": "new", "state": "active"}

    with patch("requests.post", return_value=mock_response) as mock_post:
        result = runner.invoke(app, ["create", "new", "1.1.1.1", "active"])
        assert result.exit_code == 0
        assert "new" in result.stdout
        mock_post.assert_called_once()
