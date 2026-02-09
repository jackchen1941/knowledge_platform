# Knowledge Management Platform - Development Makefile

.PHONY: help install dev test lint format clean docker-build docker-up docker-down

# Default target
help:
	@echo "Knowledge Management Platform - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     - Install all dependencies"
	@echo "  dev         - Start development servers"
	@echo "  test        - Run all tests"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code"
	@echo "  clean       - Clean build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-up   - Start Docker services"
	@echo "  docker-down - Stop Docker services"
	@echo ""
	@echo "Database:"
	@echo "  db-migrate  - Run database migrations"
	@echo "  db-upgrade  - Upgrade database to latest"
	@echo "  db-reset    - Reset database"

# Development setup
install:
	@echo "Installing backend dependencies..."
	cd backend && python -m pip install --upgrade pip
	cd backend && pip install -r requirements-dev.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Setting up pre-commit hooks..."
	cd backend && pre-commit install

# Development servers
dev:
	@echo "Starting development servers..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:3000"
	@echo "Press Ctrl+C to stop all servers"
	@make -j2 dev-backend dev-frontend

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm start

# Testing
test:
	@echo "Running backend tests..."
	cd backend && pytest -v --cov=app --cov-report=term-missing
	@echo "Running frontend tests..."
	cd frontend && npm test -- --coverage --watchAll=false

test-backend:
	cd backend && pytest -v --cov=app --cov-report=term-missing

test-frontend:
	cd frontend && npm test -- --coverage --watchAll=false

# Code quality
lint:
	@echo "Running backend linting..."
	cd backend && flake8 app
	cd backend && mypy app
	cd backend && bandit -r app
	@echo "Running frontend linting..."
	cd frontend && npm run lint

format:
	@echo "Formatting backend code..."
	cd backend && black app
	cd backend && isort app
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# Database operations
db-migrate:
	cd backend && alembic revision --autogenerate -m "Auto migration"

db-upgrade:
	cd backend && alembic upgrade head

db-reset:
	cd backend && rm -f knowledge_platform.db
	cd backend && alembic upgrade head

# Docker operations
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	cd frontend && rm -rf build node_modules/.cache
	cd backend && rm -rf .coverage htmlcov

# Production deployment
deploy-prod:
	@echo "Building production images..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
	@echo "Starting production services..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Security checks
security-check:
	@echo "Running security checks..."
	cd backend && bandit -r app -f json -o bandit-report.json
	cd backend && safety check
	cd frontend && npm audit

# Performance testing
perf-test:
	@echo "Running performance tests..."
	# Add performance testing commands here

# Backup database
backup-db:
	@echo "Creating database backup..."
	# Add database backup commands here