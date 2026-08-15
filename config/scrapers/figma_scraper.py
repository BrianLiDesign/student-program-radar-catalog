"""
Figma for Education scraper
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

HIGHER_ED_URL = "https://www.figma.com/education/higher-education/"
CANONICAL_PROGRAM_NAME = "Figma for Education"


class FigmaScraper(EnhancedBaseScraper):
    """Figma for Education (higher education) scraper."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [HIGHER_ED_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "figma.com/education" not in url:
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if "student" not in lower and "education" not in lower:
            logger.warning("Figma education page missing expected signals: %s", url)
            return None

        description = first_paragraph(soup) or (
            "Students and faculty get Figma for free with an Education plan."
        )

        apply_url = HIGHER_ED_URL
        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text(strip=True).lower()
            if "verify" in link_text or "apply" in link_text or "education/apply" in href:
                if href.startswith("http"):
                    apply_url = href
                    break
                if href.startswith("/"):
                    apply_url = f"https://www.figma.com{href}"
                    break

        status = "Rolling" if apply_url != HIGHER_ED_URL else "Unknown"

        return {
            "name": CANONICAL_PROGRAM_NAME,
            "company": self.company_name,
            "apply_url": apply_url,
            "status": status,
            "role_type": "Fellowship/Scholarship-adjacent",
            "domain": "Design/Creative",
            "eligibility_summary": (
                "Higher-education students and faculty with school-issued email (see Figma verification)"
            ),
            "location_notes": "Global (online)",
            "compensation_bucket": "Unpaid-or-perks",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "notes": "Parsed from figma.com/education/higher-education landing page.",
        }
