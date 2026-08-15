"""
IBM SkillsBuild university students scraper
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

UNIVERSITY_STUDENTS_URL = "https://skillsbuild.org/university/students"
CANONICAL_PROGRAM_NAME = "IBM SkillsBuild for University Students"


class IBMScraper(EnhancedBaseScraper):
    """IBM SkillsBuild for university students scraper."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [UNIVERSITY_STUDENTS_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "skillsbuild.org" not in url:
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if "university" not in lower and "student" not in lower:
            logger.warning("IBM SkillsBuild page missing expected signals: %s", url)
            return None

        title_elem = soup.find("h1")
        name = self._extract_text(title_elem) if title_elem else CANONICAL_PROGRAM_NAME
        if not name or len(name) > 120 or "skillsbuild" not in name.lower():
            name = CANONICAL_PROGRAM_NAME

        description = first_paragraph(soup) or (
            "Free flexible AI and career skills training for university students."
        )

        apply_url = UNIVERSITY_STUDENTS_URL
        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text(strip=True).lower()
            if "sign up" in link_text or "sign-up" in link_text:
                if href.startswith("http"):
                    apply_url = href
                    break
                if href.startswith("/"):
                    apply_url = f"https://skillsbuild.org{href}"
                    break

        status = "Rolling" if apply_url != UNIVERSITY_STUDENTS_URL else "Unknown"

        return {
            "name": name,
            "company": self.company_name,
            "apply_url": apply_url,
            "status": status,
            "role_type": "Fellowship/Scholarship-adjacent",
            "domain": "Education/EdTech",
            "eligibility_summary": "University students (see SkillsBuild for current enrollment requirements)",
            "location_notes": "Online / global",
            "compensation_bucket": "Unpaid-or-perks",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "notes": "Parsed from skillsbuild.org university students landing page.",
        }
