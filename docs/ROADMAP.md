# Roadmap

This roadmap describes planned improvements for the Student Program Radar Catalog.
Timelines are approximate and may shift based on maintainer capacity.

## Now (maintainer-managed phase)

- [x] JSON Schema validation and CI gates
- [x] Daily automated catalog refresh via pull request
- [x] Dual licensing (CC-BY data, MIT code)
- [x] Contributor docs, issue templates, and agent guidance
- [ ] Restore catalog freshness (re-run scrapers against live company pages)
- [ ] Publish first versioned GitHub Release (`v1.0.0`)

## Next (contributor-ready)

- Expand allowlist with verified company scrapers
- Issue-based program suggestions with structured triage labels
- Link liveness and freshness SLOs in monitoring workflow
- OpenSSF Scorecard baseline and dependency review on PRs

## Later (scale and depth)

- Consolidate sync and async scraper frameworks behind shared seams
- Installable Python package for framework reuse
- Retry/backoff and circuit-breaker improvements for scraper reliability
- Phase 3 contribution model: validated PRs for allowlist and targeted corrections

## Non-goals (for now)

- Direct community editing of generated catalog records
- Wiki as primary documentation
- Database backend for the canonical catalog (JSON remains source of truth)
- Multi-maintainer governance formalization

## How to influence the roadmap

Open a GitHub issue describing the problem, expected outcome, and who benefits.
Scraper contributions for allowlisted companies are always welcome — see
[CONTRIBUTING.md](../CONTRIBUTING.md).
