#!/usr/bin/env python3
"""
One-time migration of catalog program IDs to canonical UUID v5 (company|name).

Rewrites data/active/programs.json and data/archived/programs.json and publishes
a mapping file for downstream consumers.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from program_ids import generate_program_id
from scrape_programs import load_existing_programs, save_programs, separate_active_archived
from validate_data import load_schema, validate_programs

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
ACTIVE_PATH = os.path.join(PROJECT_ROOT, "data", "active", "programs.json")
ARCHIVED_PATH = os.path.join(PROJECT_ROOT, "data", "archived", "programs.json")
MIGRATIONS_DIR = os.path.join(PROJECT_ROOT, "docs", "migrations")
DEFAULT_MAPPING_JSON = os.path.join(MIGRATIONS_DIR, "2026-08-07-program-id-uuid-v5.json")
DEFAULT_MAPPING_MD = os.path.join(MIGRATIONS_DIR, "2026-08-07-program-id-uuid-v5.md")


@dataclass(frozen=True)
class IdMappingEntry:
    old_id: str
    new_id: str
    company: str
    name: str

    @property
    def key(self) -> str:
        return f"{self.company.strip().lower()}|{self.name.strip().lower()}"


def build_mapping(programs: list[dict]) -> list[IdMappingEntry]:
    """Build old→new ID mapping; raise if two programs collide on the same new ID."""
    entries: list[IdMappingEntry] = []
    new_id_to_old: dict[str, str] = {}

    for program in programs:
        company = program.get("company", "")
        name = program.get("name", "")
        old_id = program.get("id")
        if not old_id:
            raise SystemExit(f"Program missing id: {company} | {name}")

        new_id = generate_program_id(company, name)
        if new_id in new_id_to_old and new_id_to_old[new_id] != old_id:
            raise SystemExit(
                f"Collision: programs {new_id_to_old[new_id]} and {old_id} "
                f"both map to {new_id} ({company}|{name})"
            )
        new_id_to_old[new_id] = old_id
        entries.append(IdMappingEntry(old_id=old_id, new_id=new_id, company=company, name=name))

    return entries


def apply_mapping(programs: list[dict], mapping: list[IdMappingEntry]) -> list[dict]:
    """Return programs with canonical UUID v5 IDs."""
    old_to_new = {entry.old_id: entry.new_id for entry in mapping}
    updated: list[dict] = []

    for program in programs:
        prog = dict(program)
        old_id = prog.get("id")
        if old_id not in old_to_new:
            raise SystemExit(f"No mapping for program id {old_id}")
        prog["id"] = old_to_new[old_id]
        updated.append(prog)

    return updated


def mapping_to_json(mapping: list[IdMappingEntry], migrated_on: str) -> dict:
    return {
        "migration": "program-id-uuid-v5",
        "migrated_on": migrated_on,
        "namespace": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "key_format": "company|name (lowercase, trimmed)",
        "entries": [
            {
                "old_id": entry.old_id,
                "new_id": entry.new_id,
                "company": entry.company,
                "name": entry.name,
                "key": entry.key,
            }
            for entry in mapping
        ],
    }


def mapping_to_markdown(mapping: list[IdMappingEntry], migrated_on: str) -> str:
    lines = [
        "# Program ID migration — UUID v5 (2026-08-07)",
        "",
        "One-time migration from legacy placeholder UUIDs to canonical UUID v5 IDs",
        "derived from `company|name` via `scripts/program_ids.py`.",
        "",
        f"**Migrated on:** {migrated_on}",
        "",
        "## Downstream consumers",
        "",
        "- Merge/update key is now the canonical UUID v5 for `company|name`.",
        "- No further ID changes are planned without a new migration.",
        "",
        "## Mapping",
        "",
        "| Old ID | New ID (UUID v5) | Company | Name | Key |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in mapping:
        lines.append(
            f"| `{entry.old_id}` | `{entry.new_id}` | {entry.company} | "
            f"{entry.name} | `{entry.key}` |"
        )
    lines.append("")
    return "\n".join(lines)


def write_mapping_docs(
    mapping: list[IdMappingEntry],
    migrated_on: str,
    json_path: str = DEFAULT_MAPPING_JSON,
    md_path: str = DEFAULT_MAPPING_MD,
) -> None:
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(mapping_to_json(mapping, migrated_on), f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(mapping_to_markdown(mapping, migrated_on))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing catalog or mapping files",
    )
    parser.add_argument(
        "--migrated-on",
        default=date.today().isoformat(),
        help="ISO date stamped on mapping docs (default: today)",
    )
    args = parser.parse_args(argv)

    active = load_existing_programs(ACTIVE_PATH)
    archived = load_existing_programs(ARCHIVED_PATH)
    combined = active + archived

    if not combined:
        print("No programs to migrate.")
        return 0

    mapping = build_mapping(combined)
    migrated = apply_mapping(combined, mapping)
    new_active, new_archived = separate_active_archived(migrated)

    changed = sum(1 for entry in mapping if entry.old_id != entry.new_id)
    print(f"Programs: {len(combined)} total; {changed} IDs will change")

    schema = load_schema()
    active_errors = validate_programs(new_active, schema)
    archived_errors = validate_programs(new_archived, schema)
    if active_errors or archived_errors:
        print("Validation failed; refusing to write.")
        for err in (active_errors + archived_errors)[:10]:
            print(f"  - {err}")
        return 1

    for entry in mapping:
        if entry.old_id != entry.new_id:
            print(f"  {entry.old_id} -> {entry.new_id} | {entry.company} | {entry.name}")

    if args.dry_run:
        print("Dry run only; no files written.")
        return 0

    save_programs(ACTIVE_PATH, new_active)
    save_programs(ARCHIVED_PATH, new_archived)
    write_mapping_docs(mapping, args.migrated_on)
    print(f"Wrote {ACTIVE_PATH}")
    print(f"Wrote {ARCHIVED_PATH}")
    print(f"Wrote {DEFAULT_MAPPING_JSON}")
    print(f"Wrote {DEFAULT_MAPPING_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
