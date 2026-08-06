# ADR-0004: Sync framework as canonical scraper base

## Status

Accepted

## Context

The repository has two scraper frameworks: `scripts/scraper_framework.py` (sync) and
`scripts/scraper_framework_async.py` (async). Both duplicate caching, rate limiting,
ID generation, and fetch logic.

## Decision

- **`EnhancedBaseScraper` in `scraper_framework.py` is canonical** for all new scrapers.
- `scraper_framework_async.py` remains for batch/high-concurrency operations only.
- Shared logic (program IDs, retry semantics) lives in dedicated modules (`program_ids.py`).
- Full framework merge is deferred until async scrapers are actively used in CI.

## Consequences

- New scrapers subclass `EnhancedBaseScraper` only.
- Async framework imports `generate_program_id` from the shared module.
- Future work may extract HTTP client, cache, and rate limiter into shared submodules.
