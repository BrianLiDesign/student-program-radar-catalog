#!/usr/bin/env python3
"""Mocked tests for the UiPath and Wolfram expansion scrapers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "config" / "scrapers"))

from uipath_scraper import CANONICAL_PROGRAM_NAME as UIPATH_PROGRAM_NAME  # noqa: E402
from uipath_scraper import STUDENT_DEVELOPERS_URL, UiPathScraper  # noqa: E402
from wolfram_scraper import CANONICAL_PROGRAM_NAME as WOLFRAM_PROGRAM_NAME  # noqa: E402
from wolfram_scraper import STUDENT_AMBASSADOR_URL, WolframScraper  # noqa: E402

from program_ids import generate_program_id  # noqa: E402

UIPATH_APPLY_URL = "https://forms.gle/XcpAyFn8ZiLzY6K79"
WOLFRAM_APPLY_PATH = "/company/careers/opportunities/#op-105148-student-ambassador-program-"
WOLFRAM_APPLY_URL = f"https://www.wolfram.com{WOLFRAM_APPLY_PATH}"

UIPATH_HTML = f"""
<html><body>
<h1>UiPath Student Developer Champions</h1>
<p>The UiPath Student Developer Champions Program is a global initiative for university students
who build campus automation communities and inspire their peers.</p>
<h2>Eligibility Criteria</h2>
<p>Applicants must be full-time students at an accredited university or higher education
institution and should have at least 1.5 years remaining on campus.</p>
<a href="{UIPATH_APPLY_URL}">Apply Now</a>
</body></html>
"""

WOLFRAM_HTML = f"""
<html><body>
<h1>Wolfram Student Ambassador Initiative</h1>
<p>The Wolfram Student Ambassador Initiative gives students opportunities to teach and inspire
others to use Wolfram technology while developing technical and leadership skills.</p>
<p>High-school and university students from all over the world may apply.</p>
<a href="{WOLFRAM_APPLY_PATH}">Apply Now</a>
</body></html>
"""

REQUIRED_FIELDS = {
    "id",
    "name",
    "company",
    "apply_url",
    "status",
    "role_type",
    "domain",
    "eligibility_summary",
    "location_notes",
    "compensation_bucket",
    "last_verified",
    "short_description",
}


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


class UiPathWolframExpansionTests(unittest.TestCase):
    def test_uipath_scraper_parses_live_program_signals(self):
        scraper = UiPathScraper("UiPath", "https://www.uipath.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(UIPATH_HTML)):
            programs = scraper.scrape_programs()

        self.assertEqual(len(programs), 1)
        program = programs[0]
        self.assertTrue(REQUIRED_FIELDS.issubset(program))
        self.assertEqual(program["name"], UIPATH_PROGRAM_NAME)
        self.assertEqual(program["apply_url"], UIPATH_APPLY_URL)
        self.assertEqual(program["status"], "Accepting")
        self.assertEqual(program["id"], generate_program_id("UiPath", UIPATH_PROGRAM_NAME))

    def test_uipath_scraper_fails_closed_without_program_identity(self):
        scraper = UiPathScraper("UiPath", "https://www.uipath.com")
        html = "<html><body><h1>UiPath Community</h1><p>University events</p></body></html>"
        with patch.object(scraper, "_fetch_page", return_value=_soup(html)):
            program = scraper.parse_program_page(STUDENT_DEVELOPERS_URL)

        self.assertIsNone(program)

    def test_wolfram_scraper_parses_live_program_signals(self):
        scraper = WolframScraper("Wolfram", "https://www.wolfram.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(WOLFRAM_HTML)):
            programs = scraper.scrape_programs()

        self.assertEqual(len(programs), 1)
        program = programs[0]
        self.assertTrue(REQUIRED_FIELDS.issubset(program))
        self.assertEqual(program["name"], WOLFRAM_PROGRAM_NAME)
        self.assertEqual(program["apply_url"], WOLFRAM_APPLY_URL)
        self.assertEqual(program["status"], "Accepting")
        self.assertEqual(program["id"], generate_program_id("Wolfram", WOLFRAM_PROGRAM_NAME))

    def test_wolfram_scraper_fails_closed_without_program_identity(self):
        scraper = WolframScraper("Wolfram", "https://www.wolfram.com")
        html = "<html><body><h1>Wolfram Careers</h1><p>Student opportunities</p></body></html>"
        with patch.object(scraper, "_fetch_page", return_value=_soup(html)):
            program = scraper.parse_program_page(STUDENT_AMBASSADOR_URL)

        self.assertIsNone(program)

    def test_scrapers_reject_unrelated_urls_without_fetching(self):
        uipath = UiPathScraper("UiPath", "https://www.uipath.com")
        wolfram = WolframScraper("Wolfram", "https://www.wolfram.com")
        with patch.object(uipath, "_fetch_page") as uipath_fetch:
            self.assertIsNone(uipath.parse_program_page("https://www.uipath.com/careers"))
            uipath_fetch.assert_not_called()
        with patch.object(wolfram, "_fetch_page") as wolfram_fetch:
            self.assertIsNone(wolfram.parse_program_page("https://www.wolfram.com/products/"))
            wolfram_fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
