# Creating a release

The catalog is versioned with semantic tags (`v1.0.0`, `v1.1.0`, etc.).

## Prerequisites

- `main` passes CI
- [CHANGELOG.md](../CHANGELOG.md) updated for the release version
- `gh` CLI authenticated (`gh auth login`)

## Steps

```bash
# 1. Ensure clean state
make lint test validate e2e

# 2. Update CHANGELOG (move Unreleased items under the new version)

# 3. Commit and push
git add CHANGELOG.md
git commit -m "chore: prepare release v1.0.0"
git push origin main

# 4. Create and push tag (triggers release.yml)
git tag -a v1.0.0 -m "Student Program Radar Catalog v1.0.0"
git push origin v1.0.0
```

Alternatively, trigger a manual release from the Actions tab using the
**Release catalog snapshot** workflow with version `v1.0.0`.

## Release artifacts

- `student-program-radar-catalog-<version>.zip` — catalog bundle
- `programs.csv` — flat export of active programs
- `metadata.json` — version, timestamp, program count
- `programs.json` / `archived-programs.json` — raw JSON

## License in releases

- Dataset artifacts: CC-BY 4.0
- Code in the repository: MIT (see [NOTICE](../NOTICE))
