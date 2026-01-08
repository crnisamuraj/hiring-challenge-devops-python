.PHONY: help install dev test lint format run clean docker-up docker-down docker-test

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install .

dev:  ## Install development dependencies
	pip install -e ".[test]"

test:  ## Run tests
	pytest -v

lint:  ## Run linter (ruff)
	ruff check .

format:  ## Format code (ruff)
	ruff format .

run:  ## Run the API locally
	uvicorn app.main:app --reload

clean:  ## Clean up cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Podman commands
podman-up:  ## Start the stack with Podman
	podman compose up -d --build

podman-down:  ## Stop the stack
	podman compose down

podman-test:  ## Run tests in container
	podman compose exec api pytest -v
