.PHONY: help install dev-install lint format test clean docker-up docker-down

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	uv sync
	uv run pip install -e .

dev-install:  ## Install development dependencies
	uv sync --dev
	uv run pip install -e .
	uv run pre-commit install

lint:  ## Run linting
	uv run ruff check llm_proxy_cli/
	uv run mypy llm_proxy_cli/
	uv run markdownlint *.md

format:  ## Format code
	uv run black llm_proxy_cli/
	uv run ruff format llm_proxy_cli/
	uv run ruff check --fix llm_proxy_cli/

test:  ## Run tests
	uv run pytest tests/ -v --cov=llm_proxy_cli --cov-report=html --cov-report=term

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

docker-up:  ## Start Docker containers
	docker-compose up -d

docker-down:  ## Stop Docker containers
	docker-compose down

docker-logs:  ## Show Docker logs
	docker-compose logs -f

pre-commit:  ## Run pre-commit on all files
	uv run pre-commit run --all-files