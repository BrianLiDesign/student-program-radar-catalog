# Context

Domain glossary for the Student Program Radar Catalog. Use these terms consistently
in code, docs, issues, and architecture discussions.

## Catalog

The published dataset in `data/active/programs.json` and `data/archived/programs.json`.
The catalog is the **source of truth** for downstream consumers (e.g. student-program-radar).

## Program

A single student-facing opportunity (ambassador, campus rep, fellowship, etc.) represented
as one JSON object conforming to `data/schema.json`.

## Program ID

A stable UUID v5 identifier derived from normalized `company|name` via
`scripts/program_ids.py`. IDs must not change when a program is updated.

## Allowlist

`config/allowlist.json` — the set of companies approved for automated scraping.
Only allowlisted companies have scrapers.

## Scraper

A company-specific class in `config/scrapers/` that subclasses `EnhancedBaseScraper`,
discovers program URLs, and parses them into schema-compliant records.

## Verification

The `last_verified` date on a program record. Monitoring checks flag programs not
verified within the freshness SLO (default: 60 days).

## Refresh

The daily automation that re-scrapes allowlisted companies and opens a PR on
`automation/daily-catalog-refresh` — never pushes directly to `main`.

## Contribution phases

1. **Maintainer-managed** (current): automation + maintainers edit catalog; community submits issues and scrapers.
2. **Issue-based suggestions**: structured triage of program suggestions.
3. **Validated PRs**: targeted allowlist and correction PRs with review.

## License split

- **Data** (`data/`): CC-BY 4.0
- **Code** (everything else): MIT
