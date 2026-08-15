# Development Guide

This guide covers local setup, testing, and development workflows for the
Student Program Radar Catalog automation system.

## Prerequisites

- Python 3.9 or newer (3.13 recommended for local development)
- Git
- Network access for scraper development and end-to-end tests

## Setup

```bash
git clone https://github.com/BrianLiDesign/student-program-radar-catalog.git
cd student-program-radar-catalog
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
pre-commit install
```

## Common commands

Use the Makefile for the canonical entrypoints:

```bash
make install    # Install runtime + dev dependencies
make lint       # Run Ruff lint and format checks
make test       # Run pytest
make validate   # Validate catalog against schema
make e2e        # Run end-to-end verification
make scrape     # Refresh catalog data locally
make dq         # Run the data quality pipeline
```

Equivalent manual commands:

```bash
python -m compileall -q scripts config
python -m ruff check scripts config test_*.py
python -m ruff format --check scripts config test_*.py
python -m pytest -q
python scripts/validate_data.py
python scripts/test_end_to_end.py
python scripts/scrape_programs.py
python scripts/data_quality_workflow.py
```

## Project layout

| Path | Purpose |
|------|---------|
| `data/active/programs.json` | Published active catalog (automation-managed) |
| `data/archived/programs.json` | Archived programs |
| `data/schema.json` | JSON Schema for program records |
| `config/allowlist.json` | Companies approved for scraping |
| `config/scrapers/` | Company-specific scraper implementations |
| `scripts/` | Scraper framework, validation, and automation scripts |
| `docs/` | Schema, status, roadmap, and architecture docs |

## Development rules

1. **Do not hand-edit** `data/active/programs.json` or `data/archived/programs.json`
   in pull requests. Catalog updates come from the automation pipeline or maintainer
   review of generated refresh PRs.
2. **Preserve stable program IDs** when updating scrapers. IDs are UUID v5 values
   derived from `company` + `name` (see `scripts/program_ids.py`).
3. **Add tests** for scraper logic using mocked HTTP responses or fixture data.
4. **Run `make lint test validate e2e`** before opening a pull request.
5. **Never commit secrets**, session cookies, or credentials.

## Adding a scraper

See [AUTOMATION.md](../AUTOMATION.md), [docs/SCRAPER_CHECKLIST.md](SCRAPER_CHECKLIST.md), and the reusable batch playbook [docs/ADD_COMPANIES.md](ADD_COMPANIES.md).

## Data quality pipeline

Run the full enrichment, deduplication, history, and validation pipeline:

```bash
make dq
# or
python scripts/data_quality_workflow.py --input data/active/programs.json --output data/active/programs_processed.json
```

## Troubleshooting

- **Import errors from `scripts/`**: Run commands from the repository root.
  Scrapers add `scripts/` to `sys.path` at runtime.
- **Stale cache**: Delete the `cache/` directory if scraper output looks wrong.
- **Logs**: Check `logs/scraper.log` for scraping diagnostics (gitignored).

## Related docs

- [CONTRIBUTING.md](../CONTRIBUTING.md) — contribution phases and issue guidance
- [AUTOMATION.md](../AUTOMATION.md) — GitHub Actions workflows
- [docs/SCHEMA.md](SCHEMA.md) — program record schema
- [AGENTS.md](../AGENTS.md) — AI agent instructions
