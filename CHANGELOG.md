# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-08-08

First trustworthy catalog release after Phase 1 fidelity and freshness work (epic #10).

### Added

- Contributor Covenant Code of Conduct
- Development guide, support page, and roadmap
- GitHub issue templates for program suggestions, corrections, scrapers, and bugs
- Dual licensing: CC-BY 4.0 for data, MIT for code
- `pyproject.toml`, Ruff linting, pre-commit hooks, and Makefile entrypoints
- Published `AGENTS.md` and `CLAUDE.md` for AI-assisted development
- `CONTEXT.md` and architecture decision records in `docs/adr/`
- OpenSSF Scorecard workflow, secret scanning, and dependency review
- Catalog freshness checks in the monitoring workflow
- Shared program ID generation (`scripts/program_ids.py`) using UUID v5
- Data quality CLI (`make dq`) and scraper retry/backoff improvements
- JSON Schema, validation scripts, and scraper framework
- GitHub Actions for CI, daily refresh, health monitoring, and releases
- Automated README statistics generation
- `config/candidates.json` for parked companies after allowlist audit
- `scripts/apply_allowlist_audit.py` and `scripts/migrate_program_ids.py`
- Program ID migration mapping at `docs/migrations/2026-08-07-program-id-uuid-v5.md`
- Hybrid keep-list scrapers (Adobe, Microsoft, GitHub) with mocked HTTP tests

### Changed

- README badges, license section, and repository URL consistency
- Program ID documentation aligned with UUID v5 generation contract
- One-time migration of all catalog program IDs to canonical UUID v5 (`company|name`)
- Allowlist trimmed to 3 production-scrapeable companies (Adobe, Microsoft, GitHub)
- Controlled live refresh: 5 active programs with `last_verified` within 60-day SLO
- Adobe Student Ambassador revived from archive with evidence-backed **Accepting** status

### Removed

- Six allowlist companies moved to `config/candidates.json` (not production-scrapeable)

[Unreleased]: https://github.com/BrianLiDesign/student-program-radar-catalog/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/BrianLiDesign/student-program-radar-catalog/releases/tag/v1.0.0
