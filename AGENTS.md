# AGENTS.md

Instructions for AI coding agents working on the Student Program Radar Catalog.

## Project overview

Public data catalog of U.S. college student programs (ambassadors, campus reps, fellowships, etc.).
Python 3.9+ scrapers populate `data/active/programs.json`. JSON Schema validates all records.
GitHub Actions runs CI, daily refresh PRs, health checks, and releases.

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

## Commands

```bash
make lint       # Ruff + compileall
make test       # pytest
make validate   # schema validation
make e2e        # end-to-end verification
make scrape     # refresh catalog locally
make dq         # data quality pipeline
```

## Code style

- Python 3.9 compatible syntax
- Ruff for linting and formatting (`make lint`, `make format`)
- Type hints where they clarify interfaces; no mandatory mypy yet
- Keep scraper logic in `config/scrapers/`; shared utilities in `scripts/`

## Boundaries — do not

- Hand-edit `data/active/programs.json` or `data/archived/programs.json` in PRs
- Commit secrets, cookies, API keys, or `.env` files
- Commit `memory/`, `HANDOFF*.md`, `*_SUMMARY.md`, or local demo scripts
- Bypass schema validation before saving catalog data
- Change program IDs for existing records without an explicit migration plan

## Scraper development

1. Subclass `EnhancedBaseScraper` in `config/scrapers/<company>_scraper.py`
2. Implement `find_program_urls()` and `parse_program_page(url)`
3. Register via `<Company>Scraper` naming convention
4. Add company to `config/allowlist.json`
5. Test with mocked HTTP — no live network in CI
6. See `docs/SCRAPER_CHECKLIST.md`
7. To add companies in batch, follow `docs/ADD_COMPANIES.md` (reusable playbook)

Program IDs are UUID v5 from `scripts/program_ids.py` — never hardcode arbitrary IDs.

## Testing

```bash
make lint test validate e2e
```

Test files: `test_workflow.py`, `test_scrape_programs.py`.

## Security

- Report vulnerabilities via GitHub private security advisories (see SECURITY.md)
- Treat scraped HTML as untrusted input
- Use framework rate limiting and timeouts

## Pull requests

- Run `make lint test validate e2e` before submitting
- PR template checklist must be satisfied
- Scraper PRs must not include generated catalog data changes

## Key files

| File | Purpose |
|------|---------|
| `data/schema.json` | JSON Schema |
| `scripts/scraper_framework.py` | Scraper base class |
| `scripts/validate_data.py` | Schema validator |
| `scripts/program_ids.py` | UUID v5 ID generation |
| `CONTEXT.md` | Domain glossary |
| `docs/ADD_COMPANIES.md` | Reusable playbook to expand the allowlist |
| `docs/adr/` | Architecture decisions |

## Related docs

- [docs/ADD_COMPANIES.md](docs/ADD_COMPANIES.md)
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [AUTOMATION.md](AUTOMATION.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
