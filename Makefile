.PHONY: help install install-dev format lint test run-backend run-frontend clean setup

# Default target
help:
	@echo "AgriGuardian AI Development Commands"
	@echo "-------------------------------------"
	@echo "make setup          - Initial setup (install deps + pre-commit)"
	@echo "make install        - Install production backend dependencies"
	@echo "make install-dev    - Install development backend dependencies"
	@echo "make format         - Run ruff formatter"
	@echo "make lint           - Run ruff linter"
	@echo "make test           - Run pytest suite"
	@echo "make run-backend    - Run FastAPI dev server"
	@echo "make run-frontend   - Run Vite dev server"
	@echo "make clean          - Remove Python cache files"

setup: install install-dev
	@echo "Installing pre-commit hooks..."
	@pre-commit install
	@echo "Setup complete."

install:
	pip install -r backend/requirements.txt

install-dev:
	pip install -r backend/requirements-dev.txt

format:
	ruff format .

lint:
	ruff check . --fix

test:
	pytest

run-backend:
	uvicorn backend.src.api.server:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
