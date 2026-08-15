"""
AMD University Program scraper
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

UNIVERSITY_PROGRAM_URL = "https://www.amd.com/en/corporate/university-program.html"
CANONICAL_PROGRAM_NAME = "AMD University Program"


class AMDScraper(EnhancedBaseScraper):
    """AMD University Program scraper."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [UNIVERSITY_PROGRAM_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "amd.com" not in url or "university-program" not in url:
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if "university" not in lower and "student" not in lower:
            logger.warning("AMD university page missing expected signals: %s", url)
            return None

        title_elem = soup.find("h1")
        name = self._extract_text(title_elem) if title_elem else CANONICAL_PROGRAM_NAME
        if not name or len(name) > 120:
            name = CANONICAL_PROGRAM_NAME

        description = first_paragraph(soup) or (
            "Hub for educators, researchers, and students to access AMD resources and programs."
        )

        return {
            "name": name,
            "company": self.company_name,
            "apply_url": UNIVERSITY_PROGRAM_URL,
            "status": infer_status_from_text(text),
            "role_type": "Fellowship/Scholarship-adjacent",
            "domain": "Tech",
            "eligibility_summary": "University educators, researchers, and students (see AMD University Program)",
            "location_notes": "Global (online resources)",
            "compensation_bucket": "Unpaid-or-perks",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "notes": "Parsed from amd.com university program page.",
        }
