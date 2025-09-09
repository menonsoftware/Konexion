# Makefile for Konexion project
# Provides convenient commands for development tasks

.PHONY: help install-backend install-frontend install-all lint format type-check security-check test pre-commit pre-commit-strict clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install-all       Install dependencies for both backend and frontend"
	@echo "  install-backend   Install backend Python dependencies"
	@echo "  install-frontend  Install frontend Node.js dependencies"
	@echo "  lint              Run linting for both backend and frontend"
	@echo "  format            Format code for both backend and frontend"
	@echo "  type-check        Run type checking (backend only)"
	@echo "  security-check    Run security scanning (backend only)"
	@echo "  pre-commit        Run development pre-commit hooks (lenient)"
	@echo "  pre-commit-strict Run all pre-commit hooks (strict)"
	@echo "  clean             Clean build artifacts and caches"
	@echo "  dev-backend       Start backend development server"
	@echo "  dev-frontend      Start frontend development server"

# Installation targets
install-all: install-backend install-frontend

install-backend:
	cd konexion_backend && uv sync

install-frontend:
	cd konexion_frontend && npm install

# Code quality targets
lint:
	@echo "Linting backend..."
	cd konexion_backend && uv run ruff check .
	@echo "Linting frontend..."
	cd konexion_frontend && npm run lint

format:
	@echo "Formatting backend..."
	cd konexion_backend && uv run ruff format .
	@echo "Formatting frontend..."
	cd konexion_frontend && npm run format

type-check:
	@echo "Type checking backend..."
	cd konexion_backend && uv run mypy .

security-check:
	@echo "Running security scan..."
	cd konexion_backend && uv run bandit -r . -c ../bandit.yaml

# Pre-commit
pre-commit:
	pre-commit run --config .pre-commit-config-dev.yaml --all-files

pre-commit-strict:
	pre-commit run --config .pre-commit-config.yaml --all-files

pre-commit-install:
	pre-commit install

# Development servers
dev-backend:
	cd konexion_backend && ./run.sh

dev-frontend:
	cd konexion_frontend && npm run dev

# Cleanup
clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaning Node.js cache..."
	cd konexion_frontend && rm -rf .svelte-kit build node_modules/.cache 2>/dev/null || true
	@echo "Cleaning pre-commit cache..."
	pre-commit clean 2>/dev/null || true
