# Automation

The catalog uses GitHub Actions for pull-request validation, scheduled refreshes, health checks, and versioned snapshots.

## Workflows

- `.github/workflows/ci-cd.yml` runs compilation, the complete test suite, schema validation, and the end-to-end verification on pull requests and pushes to `main`.
- `.github/workflows/daily-scraping.yml` refreshes data daily at 02:00 UTC. It validates and tests the result, then opens or updates `automation/daily-catalog-refresh` for review. It never commits logs or pushes generated data directly to `main`.
- `.github/workflows/monitoring.yml` validates JSON, schema compliance, a non-empty active catalog, and unique IDs daily.
- `.github/workflows/release.yml` validates the repository and publishes a ZIP, CSV, metadata, and JSON snapshot for semantic version tags.

Workflow permissions are declared explicitly. CI and monitoring are read-only; refresh receives repository and pull-request write access; release receives repository-content write access.

## Local commands

```bash
python -m pip install -r requirements.txt pytest
python -m compileall -q scripts config
python -m pytest -q
python scripts/validate_data.py
python scripts/test_end_to_end.py
```

To refresh data locally:

```bash
python scripts/scrape_programs.py
python scripts/validate_data.py
python scripts/generate_dashboard.py
```

The scraper refuses to overwrite checked-in catalog files when merged output fails schema validation.

## Adding a scraper

1. Create `config/scrapers/<company>_scraper.py`.
2. Subclass `EnhancedBaseScraper` from `scripts/scraper_framework.py`.
3. Implement `find_program_urls()` and `parse_program_page(url)`.
4. Add the company and base URL to `config/allowlist.json`.
5. Ensure the class name follows `<Company>Scraper`; the registry discovers matching classes automatically.
6. Add deterministic tests that mock network responses or use fixture data.
7. Run all local commands above before opening a pull request.

Minimal shape:

```python
from scraper_framework import EnhancedBaseScraper


class ExampleScraper(EnhancedBaseScraper):
    def find_program_urls(self):
        return [f"{self.base_url}/students"]

    def parse_program_page(self, url):
        page = self._fetch_page(url)
        if page is None:
            return None
        return {
            "name": "Example Student Program",
            "apply_url": url,
            # Include every field required by data/schema.json.
        }
```

## Data safety

- Treat company pages as untrusted input.
- Use timeouts and the framework rate limiter.
- Do not store credentials or session cookies in the repository.
- Do not emit a program from a generic, error, or unrelated page.
- Preserve stable IDs when updating an existing program.
- Validate all merged active and archived records before saving.
- Review generated pull requests before merging because source pages can change unexpectedly.

Logs and caches are local diagnostics and are excluded by `.gitignore`.
