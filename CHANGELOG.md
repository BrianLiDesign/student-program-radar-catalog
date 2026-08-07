# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

### Changed

- README badges, license section, and repository URL consistency
- Program ID documentation aligned with UUID v5 generation contract
- One-time migration of all catalog program IDs to canonical UUID v5 (`company|name`); see [docs/migrations/2026-08-07-program-id-uuid-v5.md](docs/migrations/2026-08-07-program-id-uuid-v5.md)

## [1.0.0] - 2026-08-05

### Added

- Initial public catalog with 12 active programs across 9 allowlisted companies
- JSON Schema, validation scripts, and scraper framework
- GitHub Actions for CI, daily refresh, health monitoring, and releases
- Automated README statistics generation

[Unreleased]: https://github.com/BrianLiDesign/student-program-radar-catalog/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/BrianLiDesign/student-program-radar-catalog/releases/tag/v1.0.0
