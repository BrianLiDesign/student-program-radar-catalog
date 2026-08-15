"""Cengage Student Ambassador Program scraper."""

from __future__ import annotations

import logging
import os
import sys
from typing import Optional
from urllib.parse import urlparse

_scripts_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from scraper_framework import EnhancedBaseScraper
from scraper_parse_utils import page_text, snippet_from_text, today_iso

logger = logging.getLogger(__name__)

STUDENT_AMBASSADOR_URL = "https://www.cengage.com/student/ambassador/"
APPLICATION_URL = (
    "https://cengage.wd5.myworkdayjobs.com/CengageNorthAmericaCareers"
    "?locationCountry=bc33aa3152ec42d4995f4791a106ed09&q=student+ambassador"
)
CANONICAL_PROGRAM_NAME = "Cengage Student Ambassador Program"


def _is_application_link(href: str, link_text: str) -> bool:
    """Return whether a link is the public Cengage Workday application CTA."""
    parsed = urlparse(href)
    return (
        parsed.scheme == "https"
        and parsed.netloc == "cengage.wd5.myworkdayjobs.com"
        and "apply" in link_text.lower()
    )


class CengageScraper(EnhancedBaseScraper):
    """Scrape Cengage's public Student Ambassador program page."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [STUDENT_AMBASSADOR_URL]

    def parse_program_page(self, url: str) -> Optional[dict]:  # noqa: UP045 - Python 3.9
        if url != STUDENT_AMBASSADOR_URL:
            return None

        soup = self._fetch_page(url)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if "cengage student ambassador" not in lower:
            logger.warning("Cengage page missing Student Ambassador identity: %s", url)
            return None

        active_application_cta = any(
            _is_application_link(link.get("href", ""), link.get_text(" ", strip=True))
            for link in soup.find_all("a", href=True)
        )

        return {
            "name": CANONICAL_PROGRAM_NAME,
            "company": self.company_name,
            "apply_url": APPLICATION_URL,
            "status": "Accepting" if active_application_cta else "Unknown",
            "role_type": "Ambassador",
            "domain": "Education/EdTech",
            "eligibility_summary": (
                "Full-time undergraduate college or university students who have used a "
                "Cengage learning platform, are active on campus and social media, can work "
                "in North America, and can commit about three hours per week"
            ),
            "location_notes": "North America; campus-based with virtual collaboration",
            "compensation_bucket": "Paid",
            "last_verified": today_iso(),
            "short_description": (
                "Cengage Student Ambassadors help classmates use affordable learning tools "
                "through campus outreach, social content, panels, and product support."
            ),
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "time_commitment": "Average of 3 hours per week",
            "perks_detail": "$18 per hour, complimentary Cengage products, and professional development",
            "responsibilities": [
                "Support students who purchase or use Cengage products",
                "Promote Cengage course materials through campus outreach and social media",
                "Represent the student voice in focus groups, webinars, and panels",
                "Create visual and written content for Cengage",
            ],
            "social_requirements": "Active on social media and in the college community",
            "notes": "Parsed from Cengage's official Student Ambassador program page.",
        }
