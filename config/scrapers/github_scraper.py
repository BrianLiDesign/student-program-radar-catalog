#!/usr/bin/env python3
"""
GitHub Campus Expert scraper
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

CAMPUS_EXPERT_URL = "https://github.com/education/students/campus-expert"


class GitHubScraper(EnhancedBaseScraper):
    """GitHub Campus Expert scraper (hybrid: live fetch + parsed fields)."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=2.0)

    def find_program_urls(self) -> list[str]:
        return [CAMPUS_EXPERT_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "campus-expert" not in url and "campus-experts" not in url:
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        if "campus expert" not in text.lower():
            logger.warning("GitHub page missing campus expert signals: %s", url)
            return None

        title_elem = soup.find("h1")
        name = self._extract_text(title_elem) if title_elem else "GitHub Campus Expert"
        if not name or len(name) > 120:
            name = "GitHub Campus Expert"

        description = first_paragraph(soup) or (
            "GitHub Campus Experts are student leaders who build technical communities on campus."
        )

        apply_url = CAMPUS_EXPERT_URL
        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text(strip=True).lower()
            if "apply" in link_text and href.startswith("http"):
                apply_url = href
                break

        return {
            "name": name,
            "company": self.company_name,
            "apply_url": apply_url,
            "status": infer_status_from_text(text),
            "role_type": "Student Expert/Leader",
            "domain": "Tech",
            "eligibility_summary": "Students enrolled in a degree-granting institution",
            "location_notes": "Global (virtual with local events)",
            "compensation_bucket": "Unpaid-or-perks",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "notes": "Parsed from github.com/education campus expert page (Phase 1 hybrid scraper).",
        }
