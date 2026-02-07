.PHONY: help install dev run test format lint clean

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install dependencies with Poetry
	poetry install

dev:  ## Install development dependencies
	poetry install --with dev

run:  ## Run the development server
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests with coverage
	poetry run pytest --cov=app --cov-report=html --cov-report=term-missing

format:  ## Format code with black and isort
	poetry run black app/
	poetry run isort app/

lint:  ## Run linters (flake8, mypy)
	poetry run flake8 app/
	poetry run mypy app/

type-check:  ## Run type checking with mypy
	poetry run mypy app/

clean:  ## Clean up cache and build files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -f .coverage
	rm -f *.db

docker-build:  ## Build Docker image
	docker build -t health-rag-api .

docker-run:  ## Run Docker container
	docker run -p 8000:8000 --env-file .env health-rag-api

setup:  ## Initial project setup
	cp .env.example .env
	@echo "Please edit .env and add your API keys"
	@echo "Generate SECRET_KEY with: openssl rand -hex 32"
	poetry install

migrate:  ## Run database migrations (when Alembic is added)
	@echo "Migrations not yet configured. Add Alembic for this feature."

db-create:  ## Create database tables
	poetry run python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine); print('Database tables created')"

serve-prod:  ## Run production server with gunicorn
	poetry run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
