"""Princess Polly College Ambassador Program scraper."""

from __future__ import annotations

import logging
import os
import sys
from urllib.parse import urljoin

_scripts_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from scraper_framework import EnhancedBaseScraper
from scraper_parse_utils import first_paragraph, page_text, snippet_from_text, today_iso

logger = logging.getLogger(__name__)

COLLEGE_AMBASSADOR_URL = "https://us.princesspolly.com/pages/college-ambassador"
APPLICATION_URL = "https://princesspolly.aspireiq.com/join/CAP2627"
CANONICAL_PROGRAM_NAME = "Princess Polly College Ambassador Program"


def _application_link(soup) -> str | None:
    """Return the application link advertised by the official program page."""
    for link in soup.find_all("a", href=True):
        href = str(link["href"]).strip()
        link_text = link.get_text(" ", strip=True).lower()
        if href and "apply now" in link_text:
            return urljoin(COLLEGE_AMBASSADOR_URL, href)
    return None


class PrincessPollyScraper(EnhancedBaseScraper):
    """Parse Princess Polly's official College Ambassador page."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [COLLEGE_AMBASSADOR_URL]

    def parse_program_page(self, url: str) -> dict | None:
        if "us.princesspolly.com/pages/college-ambassador" not in url:
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if "princess polly" not in lower or "college ambassador program" not in lower:
            logger.warning("Princess Polly page missing College Ambassador identity: %s", url)
            return None

        discovered_apply_url = _application_link(soup)
        status = "Accepting" if discovered_apply_url else "Unknown"
        description = first_paragraph(soup) or (
            "College Ambassadors create fashion content and promote Princess Polly on campus."
        )

        return {
            "name": CANONICAL_PROGRAM_NAME,
            "company": self.company_name,
            "apply_url": discovered_apply_url or APPLICATION_URL,
            "status": status,
            "role_type": "Creator/Influencer",
            "domain": "Consumer brand",
            "eligibility_summary": (
                "Applicants must be at least 18 and enrolled full-time at a U.S. college, "
                "with an active .edu email address and public social accounts"
            ),
            "location_notes": "Open to students at U.S. and Canadian colleges",
            "compensation_bucket": "Paid",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "notes": "Parsed from Princess Polly's official College Ambassador page.",
        }
