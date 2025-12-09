############################################################
# AI Support Desk Assistant — Makefile
# Minimal, clean, senior-developer quality
############################################################

PYTHON := python3
VENV_DIR := .venv
VENV_BIN := $(VENV_DIR)/bin
PIP := $(VENV_BIN)/pip

############################################################
# 1. ENVIRONMENT MANAGEMENT
############################################################

# Check if venv exists; if not, create it
$(VENV_DIR):
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "✓ Created virtual environment in $(VENV_DIR)"

# Ensure venv is created before running any pip installs
ensure-venv: $(VENV_DIR)
	@echo "✓ Virtual environment ready"
	@echo "To activate, run: source $(VENV_BIN)/activate"

############################################################
# 2. INSTALL DEPENDENCIES
############################################################

requirements: ensure-venv
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt
	@echo "✓ Installed runtime dependencies"

requirements-dev: ensure-venv
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	@echo "✓ Installed development dependencies"

############################################################
# 3. RUN SERVICES
############################################################

run-api:
	@echo "⚠️  Remember to first activate the venv:"
	@echo "   source $(VENV_BIN)/activate"
	@echo ""
	$(VENV_BIN)/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-ingest:
	@echo "⚠️ Activate venv before running ingestion"
	$(VENV_BIN)/python scripts/ingest_docs.py

############################################################
# 4. CODE QUALITY
############################################################

format:
	$(VENV_BIN)/black app scripts

lint:
	$(VENV_BIN)/flake8 app scripts --ignore=E501,W503,E203

############################################################
# 5. UTILITY
############################################################

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "✓ Cleaned Python caches"

############################################################
# END
############################################################
