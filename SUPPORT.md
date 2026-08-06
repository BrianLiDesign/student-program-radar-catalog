# Support

## Getting help

- **Data questions** (missing programs, incorrect listings): open a
  [Program correction](.github/ISSUE_TEMPLATE/program-correction.yml) or
  [Program suggestion](.github/ISSUE_TEMPLATE/program-suggestion.yml) issue.
- **Scraper or automation bugs**: open a
  [Bug report](.github/ISSUE_TEMPLATE/bug-report.yml) issue.
- **Security concerns**: follow [SECURITY.md](SECURITY.md) — do not file public issues.
- **General questions**: open a GitHub issue with the `question` label.

## Response expectations

This project is maintainer-managed. Issues are triaged on a best-effort basis.
There is no guaranteed SLA for responses.

## Consumers of the catalog data

The canonical dataset lives in:

- `data/active/programs.json`
- `data/archived/programs.json`

Versioned snapshots are published as [GitHub Releases](https://github.com/BrianLiDesign/student-program-radar-catalog/releases)
with ZIP, CSV, and metadata attachments.

The [student-program-radar](https://github.com/brianli808/student-program-radar) web app
consumes this catalog for discovery and matching.

## Related resources

- [README.md](README.md) — overview and quick start
- [docs/ROADMAP.md](docs/ROADMAP.md) — planned improvements
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute
