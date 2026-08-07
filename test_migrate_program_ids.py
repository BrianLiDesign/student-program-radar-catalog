#!/usr/bin/env python3
"""Tests for Phase 1 WS1 program ID migration."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from migrate_program_ids import apply_mapping, build_mapping
from program_ids import generate_program_id
from scrape_programs import merge_programs


class MigrateProgramIdsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.active = json.loads(
            (PROJECT_ROOT / "data" / "active" / "programs.json").read_text(encoding="utf-8")
        )
        cls.archived = json.loads(
            (PROJECT_ROOT / "data" / "archived" / "programs.json").read_text(encoding="utf-8")
        )
        cls.mapping_path = (
            PROJECT_ROOT / "docs" / "migrations" / "2026-08-07-program-id-uuid-v5.json"
        )

    def test_checked_in_ids_match_uuid_v5(self):
        for program in self.active + self.archived:
            expected = generate_program_id(program["company"], program["name"])
            self.assertEqual(
                program["id"],
                expected,
                f"{program['company']} | {program['name']}",
            )

    def test_mapping_file_covers_all_programs(self):
        self.assertTrue(self.mapping_path.exists(), "migration mapping JSON missing")
        data = json.loads(self.mapping_path.read_text(encoding="utf-8"))
        entries = data["entries"]
        self.assertEqual(len(entries), len(self.active) + len(self.archived))

        new_ids = {entry["new_id"] for entry in entries}
        old_ids = {entry["old_id"] for entry in entries}
        catalog_ids = {program["id"] for program in self.active + self.archived}

        self.assertEqual(catalog_ids, new_ids)
        self.assertFalse(catalog_ids & old_ids)

    def test_build_mapping_detects_collisions(self):
        programs = [
            {"id": "a", "company": "Co", "name": "Program A"},
            {"id": "b", "company": "Co", "name": "Program A"},
        ]
        with self.assertRaises(SystemExit):
            build_mapping(programs)

    def test_merge_programs_updates_by_canonical_id_without_duplicates(self):
        existing = [dict(self.active[0])]
        scraped = dict(existing[0])
        scraped["short_description"] = "Updated via scrape"
        # Scrapers assign canonical IDs before merge (see scraper_framework.scrape_programs)
        scraped["id"] = generate_program_id(scraped["company"], scraped["name"])

        merged = merge_programs(existing, [scraped])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["id"], existing[0]["id"])
        self.assertEqual(merged[0]["short_description"], "Updated via scrape")

    def test_apply_mapping_rewrites_ids(self):
        sample = [
            {
                "id": "legacy-1",
                "company": "Microsoft",
                "name": "Microsoft Learn Student Ambassador",
                "status": "Unknown",
            }
        ]
        mapping = build_mapping(sample)
        updated = apply_mapping(sample, mapping)
        self.assertEqual(
            updated[0]["id"],
            generate_program_id("Microsoft", "Microsoft Learn Student Ambassador"),
        )


if __name__ == "__main__":
    unittest.main()
