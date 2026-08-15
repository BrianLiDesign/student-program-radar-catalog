"""
Google GDG on Campus / developer community scraper
"""

from __future__ import annotations

import logging
import os
import sys

_scripts_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from scraper_framework import EnhancedBaseScraper
from scraper_parse_utils import first_paragraph, page_text, snippet_from_text, today_iso

logger = logging.getLogger(__name__)

COMMUNITY_URL = "https://developers.google.com/community"
CANONICAL_PROGRAM_NAME = "Google Developer Groups on Campus Lead"


class GoogleScraper(EnhancedBaseScraper):
    """Google developer community scraper (GDG on Campus lead program)."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [COMMUNITY_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "developers.google.com" not in url:
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if "developer group" not in lower and "gdg" not in lower:
            logger.warning("Google community page missing GDG signals: %s", url)
            return None

        description = first_paragraph(soup) or (
            "Lead a Google Developer Group on campus and grow a local developer community."
        )

        apply_url = COMMUNITY_URL
        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text(strip=True).lower()
            if href.startswith("http") and ("apply" in link_text or "lead" in link_text):
                apply_url = href
                break

        status = "Accepting" if apply_url != COMMUNITY_URL else "Unknown"

        return {
            "name": CANONICAL_PROGRAM_NAME,
            "company": self.company_name,
            "apply_url": apply_url,
            "status": status,
            "role_type": "Student Expert/Leader",
            "domain": "Tech",
            "eligibility_summary": (
                "University students who can lead or start a Google Developer Group on campus"
            ),
            "location_notes": "Campus-based (global program)",
            "compensation_bucket": "Unpaid-or-perks",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "notes": "Parsed from developers.google.com/community (GDG on Campus lead content).",
        }
