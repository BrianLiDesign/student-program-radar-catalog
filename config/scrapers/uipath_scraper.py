"""UiPath Student Developer Champions scraper."""

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

STUDENT_DEVELOPERS_URL = "https://community.uipath.com/uipath-student-developers-program/"
CANONICAL_PROGRAM_NAME = "UiPath Student Developer Champions"


class UiPathScraper(EnhancedBaseScraper):
    """Scrape UiPath's university Student Developer Champions program."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [STUDENT_DEVELOPERS_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "community.uipath.com/uipath-student-developers-program" not in url.lower():
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if "student developer champion" not in lower or "university" not in lower:
            logger.warning("UiPath page missing Student Developer Champions identity: %s", url)
            return None

        apply_url = STUDENT_DEVELOPERS_URL
        for link in soup.find_all("a", href=True):
            href = link["href"].strip()
            link_text = link.get_text(" ", strip=True).lower()
            if href.startswith("http") and "apply" in link_text:
                apply_url = href
                break

        description = first_paragraph(soup) or (
            "University students lead automation communities, events, and peer learning as "
            "UiPath Student Developer Champions."
        )

        return {
            "name": CANONICAL_PROGRAM_NAME,
            "company": self.company_name,
            "apply_url": apply_url,
            "status": "Accepting" if apply_url != STUDENT_DEVELOPERS_URL else "Unknown",
            "role_type": "Student Expert/Leader",
            "domain": "Tech",
            "eligibility_summary": (
                "Full-time students at accredited universities or higher-education institutions "
                "with at least 1.5 years remaining on campus"
            ),
            "location_notes": "Campus-based global program; U.S. university students are eligible",
            "compensation_bucket": "Unpaid-or-perks",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "notes": (
                "Parsed from UiPath's official Student Developer Champions program page. "
                "Selections favor institutions without an active champion."
            ),
        }
