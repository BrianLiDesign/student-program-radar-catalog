"""Red Bull Student Marketeer scraper."""

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

STUDENT_MARKETEER_URL = "https://jobs.redbull.com/us-en/microsite/student-marketeer?lang=en"
APPLICATION_URL = (
    "https://jobs.redbull.com/us-en/results?functionNames=Student+Jobs&functions=10"
    "&keywords=&locationNames=North+America&locations=2049"
)
CANONICAL_PROGRAM_NAME = "Red Bull Student Marketeer"


def _application_link(soup) -> str | None:
    """Return a public application link only when the page labels it as such."""
    for link in soup.find_all("a", href=True):
        href = str(link["href"]).strip()
        link_text = link.get_text(" ", strip=True).lower()
        if href and "apply now" in link_text:
            return urljoin(STUDENT_MARKETEER_URL, href)
    return None


class RedBullScraper(EnhancedBaseScraper):
    """Parse Red Bull's official U.S. Student Marketeer program page."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [STUDENT_MARKETEER_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "jobs.redbull.com/us-en/microsite/student-marketeer" not in url:
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if "student marketeer" not in lower:
            logger.warning("Red Bull page missing Student Marketeer identity: %s", url)
            return None

        discovered_apply_url = _application_link(soup)
        status = "Accepting" if discovered_apply_url else "Unknown"
        description = first_paragraph(soup) or (
            "Student Marketeers represent Red Bull through campus marketing, events, and outreach."
        )

        return {
            "name": CANONICAL_PROGRAM_NAME,
            "company": self.company_name,
            "apply_url": discovered_apply_url or APPLICATION_URL,
            "status": status,
            "role_type": "Campus Rep",
            "domain": "Consumer brand",
            "eligibility_summary": (
                "University students who can represent Red Bull on and around their campus"
            ),
            "location_notes": "Campus-based roles at participating U.S. universities",
            "compensation_bucket": "Paid",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": True,
            "notes": "Parsed from Red Bull's official U.S. Student Marketeer page.",
        }
