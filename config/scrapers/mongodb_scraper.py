"""
MongoDB for Students scraper
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

STUDENTS_URL = "https://www.mongodb.com/students"
CANONICAL_PROGRAM_NAME = "MongoDB for Students"


class MongoDBScraper(EnhancedBaseScraper):
    """MongoDB for Students / Student Pack scraper."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [STUDENTS_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "mongodb.com/students" not in url:
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if "student" not in lower:
            logger.warning("MongoDB students page missing expected signals: %s", url)
            return None

        description = first_paragraph(soup) or (
            "MongoDB for Students offers free Atlas credits, certifications, and learning resources."
        )

        apply_url = STUDENTS_URL
        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text(strip=True).lower()
            if href.startswith("http") and ("apply" in link_text or "sign up" in link_text):
                apply_url = href
                break

        return {
            "name": CANONICAL_PROGRAM_NAME,
            "company": self.company_name,
            "apply_url": apply_url,
            "status": infer_status_from_text(text),
            "role_type": "Fellowship/Scholarship-adjacent",
            "domain": "Tech",
            "eligibility_summary": "Students eligible for MongoDB for Students / Student Pack benefits",
            "location_notes": "Online / global",
            "compensation_bucket": "Unpaid-or-perks",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "notes": "Parsed from mongodb.com/students (Student Pack and student learning resources).",
        }
