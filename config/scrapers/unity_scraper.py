"""
Unity Education scraper
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

EDUCATION_URL = "https://unity.com/solutions/education"
CANONICAL_PROGRAM_NAME = "Unity Education"


class UnityScraper(EnhancedBaseScraper):
    """Unity Education scraper."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [EDUCATION_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "unity.com/solutions/education" not in url:
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if "education" not in lower and "student" not in lower:
            logger.warning("Unity education page missing expected signals: %s", url)
            return None

        description = first_paragraph(soup) or (
            "Unity Education helps students learn real-time 3D skills for games, XR, and interactive media."
        )

        apply_url = EDUCATION_URL
        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text(strip=True).lower()
            if href.startswith("http") and ("get started" in link_text or "contact" in link_text):
                apply_url = href
                break

        return {
            "name": CANONICAL_PROGRAM_NAME,
            "company": self.company_name,
            "apply_url": apply_url,
            "status": infer_status_from_text(text),
            "role_type": "Fellowship/Scholarship-adjacent",
            "domain": "Education/EdTech",
            "eligibility_summary": "Students and educators teaching real-time 3D development",
            "location_notes": "Global (online)",
            "compensation_bucket": "Unpaid-or-perks",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "notes": "Parsed from unity.com/solutions/education.",
        }
