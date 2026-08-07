"""
Adobe scraper for Student Program Radar Catalog
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

STUDENT_AMBASSADOR_URL = "https://www.adobeforeducation.com/student-ambassador-program"


class AdobeScraper(EnhancedBaseScraper):
    """Adobe Student Ambassador scraper (hybrid: live fetch + parsed fields)."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [STUDENT_AMBASSADOR_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "student-ambassador" not in url:
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        if "student ambassador" not in text.lower():
            logger.warning("Adobe page missing expected student ambassador signals: %s", url)
            return None

        title_elem = soup.find("h1")
        name = self._extract_text(title_elem) if title_elem else "Adobe Student Ambassador"
        if not name or len(name) > 120:
            name = "Adobe Student Ambassador"

        description = first_paragraph(soup) or (
            "Student ambassadors represent Adobe on campus and share creative tools with peers."
        )

        apply_url = STUDENT_AMBASSADOR_URL
        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text(strip=True).lower()
            if href.startswith("http") and ("apply" in link_text or "adobe.ly" in href.lower()):
                apply_url = href
                break

        return {
            "name": name,
            "company": self.company_name,
            "apply_url": apply_url,
            "status": infer_status_from_text(text),
            "role_type": "Ambassador",
            "domain": "Design/Creative",
            "eligibility_summary": (
                "Students at accredited institutions (see program page for current requirements)"
            ),
            "location_notes": "Campus-based with virtual components",
            "compensation_bucket": "Unpaid-or-perks",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "notes": "Parsed from adobeforeducation.com student ambassador hub (Phase 1 hybrid scraper).",
        }
