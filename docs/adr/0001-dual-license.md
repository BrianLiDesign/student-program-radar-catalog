# ADR-0001: Dual license for data and code

## Status

Accepted

## Context

The repository contains both a public dataset (`data/`) and automation code (scrapers,
scripts, CI). CC-BY 4.0 is appropriate for the dataset but not for code. A single
license left GitHub showing "Other" and confused contributors.

## Decision

- Dataset files under `data/` remain **CC-BY 4.0** ([LICENSE](../LICENSE)).
- All other files are **MIT** ([LICENSE-CODE](../LICENSE-CODE)).
- [NOTICE](../NOTICE) summarizes the split.

## Consequences

- Consumers must attribute the dataset per CC-BY when redistributing data.
- Code can be reused under MIT terms.
- Release metadata should reference both licenses.
