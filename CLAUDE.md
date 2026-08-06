# Claude Code Configuration

Read and follow [AGENTS.md](AGENTS.md) for all build, test, style, and boundary rules.

## Claude-specific notes

- Use **context7-mcp** for current library docs (requests, beautifulsoup4, jsonschema, aiohttp).
- Use **diagnose** for scraper failures; **tdd** for new scraper tests.
- Use **to-issues** to break large plans into GitHub issues.
- Recommended MCPs: context7 (library docs), github (PRs/issues).

## Quick reference

```bash
make lint test validate e2e
```

Do not edit catalog JSON by hand. Scraper contributions go in `config/scrapers/`.
