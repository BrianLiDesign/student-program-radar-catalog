# ADR-0002: Program IDs as UUID v5

## Status

Accepted

## Context

Documentation claimed UUID v5 IDs, but the scraper framework generated slug-style IDs.
Checked-in seed data used placeholder sequential UUIDs. Consumers need stable,
deterministic identifiers across scraper runs.

## Decision

- Canonical ID generation lives in `scripts/program_ids.py`.
- Key: normalized `company|name` (lowercase, trimmed).
- Namespace: fixed catalog UUID (`CATALOG_NAMESPACE`).
- Algorithm: `uuid.uuid5(namespace, key)`.
- Scrapers must not hardcode IDs; the framework assigns them when missing.
- Legacy placeholder UUIDs in seed data remain until automation refresh replaces them.

## Consequences

- Same program always gets the same ID after refresh.
- ID changes require an explicit migration (out of scope for routine scraper updates).
- Tests assert UUID format, not slug format.
- **2026-08-07:** Legacy placeholder UUIDs migrated to canonical UUID v5 via `scripts/migrate_program_ids.py`. Mapping published at [docs/migrations/2026-08-07-program-id-uuid-v5.md](../migrations/2026-08-07-program-id-uuid-v5.md).
