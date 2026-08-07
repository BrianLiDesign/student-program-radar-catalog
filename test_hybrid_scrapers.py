#!/usr/bin/env python3
"""Mocked HTTP tests for Phase 1 hybrid keep-list scrapers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "config" / "scrapers"))

from adobe_scraper import STUDENT_AMBASSADOR_URL, AdobeScraper
from github_scraper import CAMPUS_EXPERT_URL, GitHubScraper
from microsoft_scraper import IMAGINE_CUP_URL, LEAP_URL, MSA_URL, MicrosoftScraper

from program_ids import generate_program_id
from scraper_parse_utils import infer_status_from_text

ADOBE_HTML = """
<html><body>
<h1>Adobe Student Ambassador Program</h1>
<p>Lead creative communities on your campus as an Adobe Student Ambassador.</p>
<p>Applications are now open for the upcoming cohort.</p>
<a href="https://adobe.ly/apply">Apply today</a>
</body></html>
"""

MSA_HTML = """
<html><body>
<h1>Microsoft Student Ambassadors</h1>
<p>Microsoft Learn Student Ambassadors share technology with peers worldwide.</p>
<p>Apply now to join the student ambassador community.</p>
</body></html>
"""

IMAGINE_CUP_HTML = """
<html><body>
<h1>Imagine Cup</h1>
<p>Imagine Cup is a global student technology competition.</p>
</body></html>
"""

LEAP_HTML = """
<html><body>
<h1>Microsoft LEAP Apprenticeship Program</h1>
<p>LEAP is an apprenticeship program for software engineering careers.</p>
</body></html>
"""

GITHUB_HTML = """
<html><body>
<h1>Campus Experts</h1>
<p>GitHub Campus Experts build diverse technology communities on campus.</p>
<p>Become a campus expert and grow your local developer community.</p>
</body></html>
"""


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


class ScraperParseUtilsTests(unittest.TestCase):
    def test_infer_status_requires_explicit_evidence(self):
        self.assertEqual(infer_status_from_text("Applications are now open"), "Accepting")
        self.assertEqual(infer_status_from_text("Applications are closed for this year"), "Closed")
        self.assertEqual(infer_status_from_text("Learn about our student program"), "Unknown")


class HybridScraperTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)

    def test_adobe_scraper_uses_fetch_and_parses_page(self):
        scraper = AdobeScraper("Adobe", "https://www.adobeforeducation.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(ADOBE_HTML)):
            program = scraper.parse_program_page(STUDENT_AMBASSADOR_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Adobe Student Ambassador Program")
        self.assertEqual(program["status"], "Accepting")
        self.assertIn("adobe.ly", program["apply_url"])
        self.assertTrue(program["source_snippet"])

    def test_microsoft_scraper_parses_three_program_urls(self):
        scraper = MicrosoftScraper("Microsoft", "https://mvp.microsoft.com")
        fixtures = {
            MSA_URL: MSA_HTML,
            IMAGINE_CUP_URL: IMAGINE_CUP_HTML,
            LEAP_URL: LEAP_HTML,
        }

        def fake_fetch(url):
            return _soup(fixtures[url])

        with patch.object(scraper, "_fetch_page", side_effect=fake_fetch):
            programs = scraper.scrape_programs()

        self.assertEqual(len(programs), 3)
        names = {p["name"] for p in programs}
        self.assertIn("Microsoft Learn Student Ambassador", names)
        self.assertIn("Microsoft Imagine Cup", names)
        self.assertIn("Microsoft LEAP Apprenticeship Program", names)
        for program in programs:
            self.assertEqual(
                program["status"], "Accepting" if "Ambassador" in program["name"] else "Unknown"
            )

    def test_github_scraper_uses_fetch_and_keeps_unknown_without_apply_signal(self):
        scraper = GitHubScraper("GitHub", "https://github.com/education")
        with patch.object(scraper, "_fetch_page", return_value=_soup(GITHUB_HTML)):
            program = scraper.parse_program_page(CAMPUS_EXPERT_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Campus Experts")
        self.assertEqual(program["status"], "Unknown")
        self.assertEqual(program["apply_url"], CAMPUS_EXPERT_URL)

    def test_scraped_program_ids_match_canonical_uuid_v5(self):
        scraper = MicrosoftScraper("Microsoft", "https://mvp.microsoft.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(MSA_HTML)):
            program = scraper.parse_program_page(MSA_URL)

        assert program is not None
        expected_id = generate_program_id("Microsoft", "Microsoft Learn Student Ambassador")
        self.assertEqual(
            generate_program_id(program["company"], program["name"]),
            expected_id,
        )


if __name__ == "__main__":
    unittest.main()
