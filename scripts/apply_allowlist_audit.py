#!/usr/bin/env python3
"""
Apply Phase 1 WS0 allowlist-audit archive decisions.

Marks dead/unreal active catalog records as Closed with evidence in notes,
then rewrites data/active/programs.json and data/archived/programs.json.

This is the automation-friendly path for audit-driven archival (not a casual
hand-edit of generated catalog files).
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from typing import Any

# Ensure sibling imports work when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrape_programs import load_existing_programs, save_programs, separate_active_archived
from validate_data import load_schema, validate_programs

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
ACTIVE_PATH = os.path.join(PROJECT_ROOT, "data", "active", "programs.json")
ARCHIVED_PATH = os.path.join(PROJECT_ROOT, "data", "archived", "programs.json")

# Evidence from HTTP audit on 2026-08-07 (see issue #11 / epic #10).
ARCHIVE_DECISIONS: dict[str, str] = {
    "550e8400-e29b-41d4-a716-446655440000": (
        "Archived 2026-08-07 (allowlist audit #11): apply_url "
        "https://www.adobe.com/education/students/ambassador.html returned HTTP 404. "
        "Record was sample/stale; live Adobe Student Ambassador hub is "
        "https://www.adobeforeducation.com/student-ambassador-program (company kept on allowlist)."
    ),
    "550e8400-e29b-41d4-a716-446655440001": (
        "Archived 2026-08-07 (allowlist audit #11): apply_url "
        "https://www.adobe.com/education/students/creative-cloud-fellowship.html returned HTTP 404. "
        "No public replacement program page found; treated as unreal/dead sample record."
    ),
    "550e8400-e29b-41d4-a716-446655440002": (
        "Archived 2026-08-07 (allowlist audit #11): apply_url "
        "https://www.adobe.com/education/students/design-circle.html returned HTTP 404. "
        "No public replacement program page found; treated as unreal/dead sample record."
    ),
    "550e8400-e29b-41d4-a716-446655440003": (
        "Archived 2026-08-07 (allowlist audit #11): apply_url "
        "https://www.adobe.com/education/students/university-outreach.html returned HTTP 404. "
        "No public replacement program page found; treated as unreal/dead sample record."
    ),
    "550e8400-e29b-41d4-a716-446655440004": (
        "Archived 2026-08-07 (allowlist audit #11): apply_url "
        "https://www.adobe.com/education/students/ideapalooza.html returned HTTP 404. "
        "No public replacement program page found; treated as unreal/dead sample record."
    ),
    "3ba33b4a-3c1a-5555-8e1b-6b2a81b144c3": (
        "Archived 2026-08-07 (allowlist audit #11): Apple Education marketing page is not a "
        "Campus Ambassador apply program. Apple moved to config/candidates.json."
    ),
    "3ba33b4a-3c1a-5555-8e1e-6c0082cea8c9": (
        "Archived 2026-08-07 (allowlist audit #11): apply_url "
        "https://jobs.netflix.com/early_talent returned HTTP 404. No public Campus Ambassador "
        "page found. Netflix moved to config/candidates.json."
    ),
    "d290f1ee-6c54-4b01-90e6-d701748f0855": (
        "Archived 2026-08-07 (allowlist audit #11): apply_url "
        "https://www.microsoft.com/en-us/university returned HTTP 404. Dead/unreal catalog row."
    ),
    "d290f1ee-6c54-4b01-90e6-d701748f0853": (
        "Archived 2026-08-07 (allowlist audit #11): apply_url "
        "https://www.microsoft.com/en-us/garage/students/ returned HTTP 404. Dead/unreal catalog row."
    ),
}


def _append_notes(existing: Any, evidence: str) -> str:
    existing_text = (existing or "").strip()
    if not existing_text:
        return evidence
    if evidence in existing_text:
        return existing_text
    return f"{existing_text}\n\n{evidence}"


def apply_archive_decisions(
    programs: list[dict],
    decisions: dict[str, str],
    verified_on: str,
) -> tuple[list[dict], list[str]]:
    """Return updated programs and list of archived program IDs."""
    archived_ids: list[str] = []
    updated: list[dict] = []

    for program in programs:
        prog = dict(program)
        prog_id = prog.get("id")
        if prog_id in decisions:
            prog["status"] = "Closed"
            prog["last_verified"] = verified_on
            prog["notes"] = _append_notes(prog.get("notes"), decisions[prog_id])
            archived_ids.append(prog_id)
        updated.append(prog)

    missing = sorted(set(decisions) - set(archived_ids))
    if missing:
        raise SystemExit(f"Archive decisions reference unknown program IDs: {missing}")

    return updated, archived_ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing catalog files",
    )
    parser.add_argument(
        "--verified-on",
        default=date.today().isoformat(),
        help="ISO date to stamp on archived records (default: today)",
    )
    args = parser.parse_args(argv)

    active = load_existing_programs(ACTIVE_PATH)
    archived_existing = load_existing_programs(ARCHIVED_PATH)
    combined = active + archived_existing

    updated, archived_ids = apply_archive_decisions(combined, ARCHIVE_DECISIONS, args.verified_on)
    new_active, new_archived = separate_active_archived(updated)

    schema = load_schema()
    active_errors = validate_programs(new_active, schema)
    archived_errors = validate_programs(new_archived, schema)
    if active_errors or archived_errors:
        print("Validation failed; refusing to write.")
        for err in (active_errors + archived_errors)[:10]:
            print(f"  - {err}")
        return 1

    print(f"Would archive {len(archived_ids)} programs as Closed:")
    for prog_id in archived_ids:
        match = next(p for p in updated if p.get("id") == prog_id)
        print(f"  - {match.get('company')} | {match.get('name')} | {prog_id}")
    print(f"Active remaining: {len(new_active)}; archived total: {len(new_archived)}")

    if args.dry_run:
        print("Dry run only; no files written.")
        return 0

    save_programs(ACTIVE_PATH, new_active)
    save_programs(ARCHIVED_PATH, new_archived)
    print(f"Wrote {ACTIVE_PATH}")
    print(f"Wrote {ARCHIVED_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
