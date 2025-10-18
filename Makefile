# Makefile for Productivity Tracker Backend

.PHONY: help install dev-install setup format lint test test-cov run migrate upgrade downgrade clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	poetry install --only main

dev-install: ## Install all dependencies including dev tools
	poetry install
	poetry run pre-commit install

setup: dev-install ## Complete setup (install + pre-commit hooks)
	@echo "✓ Setup complete! Run 'make run' to start the server."

format: ## Format code with Black and isort
	poetry run black .
	poetry run isort .

lint: ## Run linters (Ruff, mypy, bandit)
	poetry run ruff check .
	poetry run mypy productivity_tracker
	poetry run bandit -r productivity_tracker -c pyproject.toml

test: ## Run all tests
	poetry run pytest

test-unit: ## Run unit tests only
	poetry run pytest tests/unit -m unit

test-integration: ## Run integration tests only
	poetry run pytest tests/integration -m integration

test-cov: ## Run tests with coverage report
	poetry run pytest --cov=productivity_tracker --cov-report=html --cov-report=term-missing --cov-report=xml

test-cov-unit: ## Run unit tests with coverage
	poetry run pytest tests/unit --cov=productivity_tracker --cov-report=term-missing

test-watch: ## Run tests in watch mode
	poetry run pytest-watch

test-db-up: ## Start the test database
	@echo "Starting test database..."
	docker compose -f .devcontainer/docker-compose.test.yml up -d
	@echo "Waiting for test database to be ready..."
	@sleep 5

test-db-down: ## Stop test database
	docker-compose -f .devcontainer/docker-compose.test.yml down

test-db-clean: ## Clean up test database
	@echo "Cleaning up test database..."
	docker compose -f .devcontainer/docker-compose.test.yml down -v


test-ci-full: ## Run all tests with coverage for CI environment
	@echo "Running all tests in CI mode with coverage..."
	@echo "Cleaning up old test database..."
	@$(MAKE) test-db-clean
	@echo "Starting fresh test database..."
	@$(MAKE) test-db-up
	@echo "Running tests with coverage..."
	TESTING=1 TEST_DATABASE_URL=postgresql://test_user:test_password@localhost:5433/test_productivity_tracker poetry run pytest --cov=productivity_tracker --cov-report=xml --cov-report=term-missing
	@$(MAKE) test-db-clean

run: ## Run the development server
	poetry run uvicorn productivity_tracker.main:app --reload --host 0.0.0.0 --port 8000

migrate: ## Create a new migration
	@read -p "Migration message: " message; \
	poetry run alembic revision --autogenerate -m "$$message"

upgrade: ## Run database migrations
	poetry run alembic upgrade head

downgrade: ## Rollback last migration
	poetry run alembic downgrade -1

clean: ## Clean up cache and build files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info

pre-commit: ## Run pre-commit hooks on all files
	poetry run pre-commit run --all-files

check: lint test ## Run all checks (lint + test)

ci: format lint test-cov ## Run all CI checks

.DEFAULT_GOAL := help
