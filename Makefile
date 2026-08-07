.PHONY: install install-dev lint format test validate e2e scrape dq clean help

PYTHON ?= python

help:
	@echo "Targets: install install-dev lint format test validate e2e scrape dq clean"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

install-dev: install
	$(PYTHON) -m pip install -r requirements-dev.txt
	pre-commit install

lint:
	$(PYTHON) -m ruff check scripts config test_workflow.py test_scrape_programs.py test_dashboard.py test_allowlist_audit.py test_migrate_program_ids.py test_hybrid_scrapers.py
	$(PYTHON) -m ruff format --check scripts config test_workflow.py test_scrape_programs.py test_dashboard.py test_allowlist_audit.py test_migrate_program_ids.py test_hybrid_scrapers.py
	$(PYTHON) -m compileall -q scripts config

format:
	$(PYTHON) -m ruff check --fix scripts config test_workflow.py test_scrape_programs.py test_dashboard.py test_allowlist_audit.py test_migrate_program_ids.py test_hybrid_scrapers.py
	$(PYTHON) -m ruff format scripts config test_workflow.py test_scrape_programs.py test_dashboard.py test_allowlist_audit.py test_migrate_program_ids.py test_hybrid_scrapers.py

test:
	$(PYTHON) -m pytest -q

validate:
	$(PYTHON) scripts/validate_data.py

e2e:
	$(PYTHON) scripts/test_end_to_end.py

scrape:
	$(PYTHON) scripts/scrape_programs.py

dq:
	$(PYTHON) scripts/data_quality_workflow.py

clean:
	$(PYTHON) -c "import shutil; shutil.rmtree('__pycache__', ignore_errors=True)"
	$(PYTHON) -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
