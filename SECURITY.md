# Security Policy

## Supported versions

Security fixes apply to the current `main` branch and the latest published catalog release.

## Reporting a vulnerability

Report vulnerabilities through GitHub's **private vulnerability reporting** for this repository.
Do not open a public issue for:

- Credentials or secrets exposed in the repository
- Exploitable scraper behavior (SSRF, code injection via parsed HTML)
- GitHub Actions workflow permission escalation
- Supply-chain risks in dependencies or release artifacts

Include:

1. Affected file, workflow, or component
2. Steps to reproduce
3. Expected impact
4. Suggested mitigation (if known)

The maintainer will acknowledge the report and coordinate remediation and disclosure.

## Response expectations

- Acknowledgment: within 7 days
- Status update: within 30 days
- Fix or documented mitigation for confirmed issues affecting `main`

## Scope

| In scope | Out of scope |
|----------|--------------|
| This repository's code, workflows, and release process | Third-party company websites being scraped |
| Data integrity of published catalog files | Social engineering of company program pages |
| Dependency vulnerabilities in `requirements.txt` | Issues in the consumer web app repo |

## What not to report

- Stale or incorrect program data (use a program correction issue instead)
- Scrapers failing because a company changed their website layout
- Rate limiting or blocking by target websites during normal scraping

## Secure development practices

- Never commit secrets, session cookies, or API keys
- Treat scraped HTML as untrusted input
- Keep GitHub Actions permissions at the minimum required level
- Review automation-generated PRs before merging

## Related

- [NOTICE](NOTICE) — licensing
- [AGENTS.md](AGENTS.md) — agent security boundaries
