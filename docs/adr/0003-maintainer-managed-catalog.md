# ADR-0003: Maintainer-managed catalog edits

## Status

Accepted

## Context

Allowing direct PR edits to `data/active/programs.json` risks inconsistent records,
merge conflicts with automation, and bypassed validation.

## Decision

- Catalog JSON is modified only by the automation pipeline or maintainer-reviewed refresh PRs.
- Community contributions use issues (suggestions, corrections) and scraper PRs.
- CI does not block automation PRs that update data after validation passes.

## Consequences

- Higher data consistency.
- Contributors need clear issue templates and scraper docs.
- Future phases may allow structured correction PRs (see CONTRIBUTING.md).
