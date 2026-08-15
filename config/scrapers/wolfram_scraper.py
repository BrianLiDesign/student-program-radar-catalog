"""Wolfram Student Ambassador Initiative scraper."""

from __future__ import annotations

import logging
import os
import sys
from urllib.parse import urljoin

_scripts_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from scraper_framework import EnhancedBaseScraper
from scraper_parse_utils import first_paragraph, page_text, snippet_from_text, today_iso

logger = logging.getLogger(__name__)

STUDENT_AMBASSADOR_URL = "https://www.wolfram.com/company/careers/ambassador/"
CANONICAL_PROGRAM_NAME = "Wolfram Student Ambassador Initiative"


class WolframScraper(EnhancedBaseScraper):
    """Scrape Wolfram's global student ambassador program."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [STUDENT_AMBASSADOR_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "wolfram.com/company/careers/ambassador" not in url.lower():
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if "wolfram student ambassador initiative" not in lower:
            logger.warning("Wolfram page missing Student Ambassador Initiative identity: %s", url)
            return None
        if "student" not in lower or "wolfram technolog" not in lower:
            logger.warning("Wolfram page missing expected student or technology signals: %s", url)
            return None

        apply_url = STUDENT_AMBASSADOR_URL
        for link in soup.find_all("a", href=True):
            href = link["href"].strip()
            link_text = link.get_text(" ", strip=True).lower()
            if href and "apply" in link_text:
                apply_url = urljoin(STUDENT_AMBASSADOR_URL, href)
                break

        description = first_paragraph(soup) or (
            "Student ambassadors teach and inspire others to use Wolfram technology while "
            "building technical and leadership skills."
        )

        return {
            "name": CANONICAL_PROGRAM_NAME,
            "company": self.company_name,
            "apply_url": apply_url,
            "status": "Accepting" if apply_url != STUDENT_AMBASSADOR_URL else "Unknown",
            "role_type": "Ambassador",
            "domain": "Tech",
            "eligibility_summary": (
                "High-school or university students with experience using Wolfram technologies; "
                "college applicants may be undergraduate, master's, or PhD students"
            ),
            "location_notes": "Global program with ambassadors in the United States",
            "compensation_bucket": "Unpaid-or-perks",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "time_commitment": "Typically 5-10 hours per month",
            "notes": (
                "Parsed from Wolfram's official Student Ambassador Initiative page; "
                "program membership is managed semester to semester."
            ),
        }
