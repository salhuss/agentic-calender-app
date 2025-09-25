.PHONY: setup dev test e2e lint fmt migrate seed clean help
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Install all dependencies and setup pre-commit hooks
	@echo "Setting up backend..."
	cd backend && pip install -e ".[dev]"
	@echo "Setting up frontend..."
	cd frontend && npm install
	@echo "Setting up pre-commit hooks..."
	pre-commit install
	@echo "Setup complete!"

dev: ## Start development servers with Docker Compose
	docker-compose up --build

dev-local: ## Start development servers locally (requires setup first)
	@echo "Starting backend..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Starting frontend..."
	cd frontend && npm run dev

test: ## Run all tests
	@echo "Running backend tests..."
	cd backend && python -m pytest
	@echo "Running frontend tests..."
	cd frontend && npm run test

test-backend: ## Run backend tests only
	cd backend && python -m pytest

test-frontend: ## Run frontend tests only
	cd frontend && npm run test

e2e: ## Run end-to-end tests
	@echo "Starting services for e2e tests..."
	docker-compose up -d --build
	@echo "Waiting for services to be ready..."
	sleep 10
	@echo "Running e2e tests..."
	cd frontend && npx playwright test
	@echo "Stopping services..."
	docker-compose down

lint: ## Run linting on all code
	@echo "Linting backend..."
	cd backend && ruff check .
	cd backend && mypy app
	@echo "Linting frontend..."
	cd frontend && npm run lint
	cd frontend && npm run type-check
	@echo "Checking formatting..."
	cd backend && ruff format --check .
	cd frontend && npx prettier --check .

fmt: ## Auto-format all code
	@echo "Formatting backend..."
	cd backend && ruff format .
	cd backend && ruff check --fix .
	@echo "Formatting frontend..."
	cd frontend && npx prettier --write .
	cd frontend && npm run lint:fix

migrate: ## Run database migrations
	cd backend && alembic upgrade head

seed: ## Seed database with sample data
	cd backend && python -m app.scripts.seed

clean: ## Clean up temporary files and containers
	docker-compose down -v
	docker system prune -f
	find . -type d -name "__pycache__" -delete
	find . -name "*.pyc" -delete
	rm -rf backend/.pytest_cache
	rm -rf frontend/node_modules/.cache
	rm -rf frontend/dist

build: ## Build production containers
	docker-compose -f docker-compose.prod.yml build

# Development helpers
install-backend: ## Install backend dependencies only
	cd backend && pip install -e ".[dev]"

install-frontend: ## Install frontend dependencies only
	cd frontend && npm install

check: ## Run all checks (lint + test)
	$(MAKE) lint
	$(MAKE) test