# Scraper Authoring Checklist

Use this checklist when adding or updating a company scraper.

## Before coding

- [ ] Company is on `config/allowlist.json` (or open an issue to propose addition)
- [ ] Target pages are public and do not require authentication
- [ ] You have identified stable URLs for program listings and detail pages

## Implementation

- [ ] Create `config/scrapers/<company>_scraper.py`
- [ ] Subclass `EnhancedBaseScraper` from `scripts/scraper_framework.py`
- [ ] Implement `find_program_urls()` returning a list of program page URLs
- [ ] Implement `parse_program_page(url)` returning a dict with all required schema fields
- [ ] Class name follows `<Company>Scraper` for automatic registry discovery
- [ ] Do not hardcode program IDs — let the framework generate UUID v5 IDs
- [ ] Use `_fetch_page()` / framework helpers instead of raw `requests` calls
- [ ] Respect rate limits; do not bypass caching without reason

## Required fields (from `data/schema.json`)

`id`, `name`, `company`, `apply_url`, `status`, `role_type`, `domain`,
`eligibility_summary`, `location_notes`, `compensation_bucket`, `last_verified`,
`short_description`

## Testing

- [ ] Add tests with mocked HTTP responses (no live network in CI)
- [ ] Run `make lint test validate e2e` before opening a PR
- [ ] Verify output passes `python scripts/validate_data.py`

## Pull request

- [ ] PR does not hand-edit `data/active/programs.json`
- [ ] PR description notes which company and pages were scraped
- [ ] No secrets, cookies, or credentials in the diff

## Related docs

- [AUTOMATION.md](../AUTOMATION.md)
- [docs/DEVELOPMENT.md](DEVELOPMENT.md)
- [docs/SCHEMA.md](SCHEMA.md)
