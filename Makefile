.PHONY: install install-dev test lint format seed-db run api dashboard clean help

PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff
BLACK := $(VENV)/bin/black
MYPY := $(VENV)/bin/mypy
UVICORN := $(VENV)/bin/uvicorn
STREAMLIT := $(VENV)/bin/streamlit

help:
	@echo "BlendiOS development commands:"
	@echo "  make install      Install runtime dependencies"
	@echo "  make install-dev  Install development dependencies"
	@echo "  make seed-db      Initialize SQLite database"
	@echo "  make run          Run BlendiOS desktop"
	@echo "  make api          Run FastAPI backend"
	@echo "  make dashboard    Run Streamlit dashboard"
	@echo "  make test         Run tests"
	@echo "  make lint         Run ruff and mypy"
	@echo "  make format       Format code with black and ruff"
	@echo "  make clean        Remove build artifacts"

$(VENV):
	$(PYTHON) -m venv $(VENV)

install: $(VENV)
	$(PIP) install -e .

install-dev: $(VENV)
	$(PIP) install -e ".[dev]"

seed-db: $(VENV)
	$(VENV)/bin/python scripts/seed_db.py

run: $(VENV)
	$(VENV)/bin/python -m blendios

api: $(VENV)
	$(UVICORN) blendios.api.main:app --reload

dashboard: $(VENV)
	$(STREAMLIT) run dashboards/streamlit_dashboard.py

test: $(VENV)
	$(PYTEST) tests/ -q --cov=src/blendios --cov-report=term-missing

lint: $(VENV)
	$(RUFF) check src tests dashboards
	$(MYPY) src

format: $(VENV)
	$(BLACK) src tests dashboards
	$(RUFF) check --fix src tests dashboards

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache build dist *.egg-info
