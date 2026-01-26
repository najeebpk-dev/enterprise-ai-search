.PHONY: help install install-dev setup test lint format clean run-ingest run-query docker-build docker-run

help:
	@echo "Enterprise AI Search - Available Commands"
	@echo "=========================================="
	@echo "  make install       - Install dependencies"
	@echo "  make install-dev   - Install dev dependencies"
	@echo "  make setup         - Run setup checks"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make run-ingest    - Run document ingestion"
	@echo "  make run-query     - Run query interface"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run in Docker"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

setup:
	python setup_check.py

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src --max-line-length=100
	mypy src --ignore-missing-imports

format:
	black src
	isort src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build dist .pytest_cache .coverage htmlcov .mypy_cache

run-ingest:
	python src/ingest.py

run-query:
	python src/query.py

docker-build:
	docker build -t enterprise-ai-search:latest .

docker-run:
	docker run -it --env-file .env enterprise-ai-search:latest
