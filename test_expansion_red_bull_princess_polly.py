#!/usr/bin/env python3
"""Mocked tests for the Red Bull and Princess Polly expansion scrapers."""

# ruff: noqa: E402

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "config" / "scrapers"))

from princess_polly_scraper import (
    APPLICATION_URL as PRINCESS_POLLY_APPLICATION_URL,
)
from princess_polly_scraper import COLLEGE_AMBASSADOR_URL, PrincessPollyScraper
from red_bull_scraper import APPLICATION_URL as RED_BULL_APPLICATION_URL
from red_bull_scraper import STUDENT_MARKETEER_URL, RedBullScraper

from program_ids import generate_program_id

RED_BULL_HTML = f"""
<html><body>
<h1>Become a Red Bull Student Marketeer!</h1>
<p>University students bring Red Bull to life through campus sales and marketing.</p>
<a href="{RED_BULL_APPLICATION_URL}">Apply Now</a>
</body></html>
"""

PRINCESS_POLLY_HTML = f"""
<html><body>
<h1>Princess Polly College Ambassador Program</h1>
<p>Bring Princess Polly energy to campus by creating content and sharing your code.</p>
<p>Applicants must be full-time US college students with an active .edu email.</p>
<a href="{PRINCESS_POLLY_APPLICATION_URL}">Apply Now</a>
</body></html>
"""


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


class RedBullAndPrincessPollyScraperTests(unittest.TestCase):
    def test_red_bull_parses_current_application(self):
        scraper = RedBullScraper("Red Bull", "https://jobs.redbull.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(RED_BULL_HTML)):
            program = scraper.parse_program_page(STUDENT_MARKETEER_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Red Bull Student Marketeer")
        self.assertEqual(program["status"], "Accepting")
        self.assertEqual(program["apply_url"], RED_BULL_APPLICATION_URL)

    def test_red_bull_is_unknown_without_apply_signal(self):
        html = "<h1>Red Bull Student Marketeer</h1><p>University campus marketing.</p>"
        scraper = RedBullScraper("Red Bull", "https://jobs.redbull.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(html)):
            program = scraper.parse_program_page(STUDENT_MARKETEER_URL)

        assert program is not None
        self.assertEqual(program["status"], "Unknown")

    def test_red_bull_rejects_page_without_program_identity(self):
        scraper = RedBullScraper("Red Bull", "https://jobs.redbull.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup("<h1>Student jobs</h1>")):
            program = scraper.parse_program_page(STUDENT_MARKETEER_URL)

        self.assertIsNone(program)

    def test_princess_polly_parses_current_application(self):
        scraper = PrincessPollyScraper("Princess Polly", "https://us.princesspolly.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(PRINCESS_POLLY_HTML)):
            program = scraper.parse_program_page(COLLEGE_AMBASSADOR_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Princess Polly College Ambassador Program")
        self.assertEqual(program["status"], "Accepting")
        self.assertEqual(program["apply_url"], PRINCESS_POLLY_APPLICATION_URL)

    def test_princess_polly_rejects_page_without_program_identity(self):
        scraper = PrincessPollyScraper("Princess Polly", "https://us.princesspolly.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup("<h1>New arrivals</h1>")):
            program = scraper.parse_program_page(COLLEGE_AMBASSADOR_URL)

        self.assertIsNone(program)

    def test_program_ids_are_deterministic(self):
        scraper = PrincessPollyScraper("Princess Polly", "https://us.princesspolly.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(PRINCESS_POLLY_HTML)):
            first = scraper.scrape_programs()[0]
            second = scraper.scrape_programs()[0]

        expected = generate_program_id(
            "Princess Polly", "Princess Polly College Ambassador Program"
        )
        self.assertEqual(first["id"], expected)
        self.assertEqual(second["id"], expected)


if __name__ == "__main__":
    unittest.main()
