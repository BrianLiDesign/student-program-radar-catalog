"""
Coursera for Campus scraper
"""

from __future__ import annotations

import logging
import os
import sys

_scripts_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from scraper_framework import EnhancedBaseScraper
from scraper_parse_utils import (
    first_paragraph,
    infer_status_from_text,
    page_text,
    snippet_from_text,
    today_iso,
)

logger = logging.getLogger(__name__)

CAMPUS_URL = "https://www.coursera.org/campus"
CANONICAL_PROGRAM_NAME = "Coursera for Campus"


class CourseraScraper(EnhancedBaseScraper):
    """Coursera for Campus scraper."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [CAMPUS_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "coursera.org/campus" not in url:
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if "campus" not in lower and "student" not in lower:
            logger.warning("Coursera campus page missing expected signals: %s", url)
            return None

        title_elem = soup.find("h1")
        name = self._extract_text(title_elem) if title_elem else CANONICAL_PROGRAM_NAME
        if not name or len(name) > 120 or "employability" in name.lower():
            name = CANONICAL_PROGRAM_NAME

        description = first_paragraph(soup) or (
            "Coursera for Campus equips students with in-demand skills through online learning."
        )

        apply_url = CAMPUS_URL
        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text(strip=True).lower()
            if href.startswith("http") and ("contact" in link_text or "learn more" in link_text):
                apply_url = href
                break

        return {
            "name": name,
            "company": self.company_name,
            "apply_url": apply_url,
            "status": infer_status_from_text(text),
            "role_type": "Fellowship/Scholarship-adjacent",
            "domain": "Education/EdTech",
            "eligibility_summary": "Universities and students participating in Coursera for Campus",
            "location_notes": "Online / global",
            "compensation_bucket": "Unpaid-or-perks",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "notes": "Parsed from coursera.org/campus.",
        }
