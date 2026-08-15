"""Mocked HTTP tests for the Cengage Student Ambassador scraper."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "config" / "scrapers"))

from cengage_scraper import (  # noqa: E402
    APPLICATION_URL,
    STUDENT_AMBASSADOR_URL,
    CengageScraper,
)

from program_ids import generate_program_id  # noqa: E402

ACTIVE_HTML = f"""
<html><body>
<h1>Join the Cengage Student Ambassador Program</h1>
<p>Cengage Student Ambassadors help classmates succeed in college and beyond.</p>
<p>Full-time undergraduate students work about three hours per week and earn $18/hour.</p>
<a href="{APPLICATION_URL}">Apply Now</a>
</body></html>
"""

NO_APPLICATION_HTML = """
<html><body>
<h1>Cengage Student Ambassador Program</h1>
<p>Cengage Student Ambassadors help classmates succeed in college and beyond.</p>
</body></html>
"""

UNRELATED_HTML = """
<html><body>
<h1>Cengage Student Resources</h1>
<p>Find textbooks and online learning tools for your courses.</p>
<a href="https://example.com/apply">Apply Now</a>
</body></html>
"""


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


class CengageScraperTests(unittest.TestCase):
    def setUp(self):
        self.scraper = CengageScraper("Cengage", "https://www.cengage.com")

    def test_finds_canonical_program_page(self):
        self.assertEqual(self.scraper.find_program_urls(), [STUDENT_AMBASSADOR_URL])

    def test_parses_active_program_and_workday_application(self):
        with patch.object(self.scraper, "_fetch_page", return_value=_soup(ACTIVE_HTML)):
            program = self.scraper.parse_program_page(STUDENT_AMBASSADOR_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Cengage Student Ambassador Program")
        self.assertEqual(program["status"], "Accepting")
        self.assertEqual(program["apply_url"], APPLICATION_URL)
        self.assertEqual(program["role_type"], "Ambassador")
        self.assertEqual(program["domain"], "Education/EdTech")
        self.assertEqual(program["compensation_bucket"], "Paid")

    def test_status_is_unknown_without_active_workday_apply_cta(self):
        with patch.object(
            self.scraper,
            "_fetch_page",
            return_value=_soup(NO_APPLICATION_HTML),
        ):
            program = self.scraper.parse_program_page(STUDENT_AMBASSADOR_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["status"], "Unknown")

    def test_fails_closed_when_program_identity_is_missing(self):
        with patch.object(self.scraper, "_fetch_page", return_value=_soup(UNRELATED_HTML)):
            program = self.scraper.parse_program_page(STUDENT_AMBASSADOR_URL)

        self.assertIsNone(program)

    def test_fails_closed_when_fetch_fails_or_url_is_unexpected(self):
        with patch.object(self.scraper, "_fetch_page", return_value=None):
            self.assertIsNone(self.scraper.parse_program_page(STUDENT_AMBASSADOR_URL))
        self.assertIsNone(self.scraper.parse_program_page("https://www.cengage.com/student/"))

    def test_framework_adds_deterministic_program_id(self):
        with patch.object(self.scraper, "_fetch_page", return_value=_soup(ACTIVE_HTML)):
            programs = self.scraper.scrape_programs()

        self.assertEqual(len(programs), 1)
        self.assertEqual(
            programs[0]["id"],
            generate_program_id("Cengage", "Cengage Student Ambassador Program"),
        )


if __name__ == "__main__":
    unittest.main()
