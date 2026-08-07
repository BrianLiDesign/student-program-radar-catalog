#!/usr/bin/env python3
"""Tests for Phase 1 allowlist audit (WS0)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))


class AllowlistAuditTests(unittest.TestCase):
    def test_allowlist_is_trimmed_to_scrapeable_keep_list(self):
        data = json.loads((PROJECT_ROOT / "config" / "allowlist.json").read_text(encoding="utf-8"))
        names = [c["name"] for c in data["companies"]]
        self.assertEqual(names, ["Adobe", "Microsoft", "GitHub"])
        for company in data["companies"]:
            self.assertIn("program_url", company)
            self.assertTrue(company["program_url"].startswith("https://"))

    def test_candidates_cover_parked_companies(self):
        data = json.loads((PROJECT_ROOT / "config" / "candidates.json").read_text(encoding="utf-8"))
        names = {c["name"] for c in data["candidates"]}
        self.assertEqual(
            names,
            {"Apple", "Google", "Meta", "Netflix", "Spotify", "Tesla"},
        )
        for candidate in data["candidates"]:
            self.assertTrue(candidate.get("block_reason"))
            self.assertEqual(candidate.get("date"), "2026-08-07")
            self.assertIn("suspected_program", candidate)

    def test_allowlist_and_candidates_are_disjoint(self):
        allowlist = json.loads(
            (PROJECT_ROOT / "config" / "allowlist.json").read_text(encoding="utf-8")
        )
        candidates = json.loads(
            (PROJECT_ROOT / "config" / "candidates.json").read_text(encoding="utf-8")
        )
        allow_names = {c["name"] for c in allowlist["companies"]}
        candidate_names = {c["name"] for c in candidates["candidates"]}
        self.assertFalse(allow_names & candidate_names)

    def test_archive_helper_marks_closed_with_evidence(self):
        from apply_allowlist_audit import ARCHIVE_DECISIONS, apply_archive_decisions

        sample = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Adobe Student Ambassador",
                "company": "Adobe",
                "apply_url": "https://www.adobe.com/education/students/ambassador.html",
                "status": "Unknown",
                "role_type": "Ambassador",
                "domain": "Tech",
                "eligibility_summary": "Students",
                "location_notes": "Remote",
                "compensation_bucket": "Paid",
                "last_verified": "2024-01-15",
                "short_description": "Sample",
                "notes": "Prior note",
            },
            {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Microsoft Learn Student Ambassador",
                "company": "Microsoft",
                "apply_url": "https://mvp.microsoft.com/studentambassadors",
                "status": "Unknown",
                "role_type": "Student Expert/Leader",
                "domain": "Tech",
                "eligibility_summary": "Students",
                "location_notes": "Hybrid",
                "compensation_bucket": "Unpaid-or-perks",
                "last_verified": "2024-01-20",
                "short_description": "Keep",
            },
        ]
        # Only archive the Adobe id from the full decision map for this unit test
        decisions = {
            "550e8400-e29b-41d4-a716-446655440000": ARCHIVE_DECISIONS[
                "550e8400-e29b-41d4-a716-446655440000"
            ]
        }
        updated, archived_ids = apply_archive_decisions(sample, decisions, "2026-08-07")
        self.assertEqual(archived_ids, ["550e8400-e29b-41d4-a716-446655440000"])
        self.assertEqual(updated[0]["status"], "Closed")
        self.assertIn("HTTP 404", updated[0]["notes"])
        self.assertEqual(updated[1]["status"], "Unknown")


if __name__ == "__main__":
    unittest.main()
