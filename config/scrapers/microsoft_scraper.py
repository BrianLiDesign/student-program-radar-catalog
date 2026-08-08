"""
Microsoft scraper for Student Program Radar Catalog
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

MSA_URL = "https://mvp.microsoft.com/studentambassadors"
IMAGINE_CUP_URL = "https://imaginecup.microsoft.com/en-us"
LEAP_URL = "https://leap.microsoft.com/en-US/"

PROGRAM_CONFIG = {
    MSA_URL: {
        "name": "Microsoft Learn Student Ambassador",
        "role_type": "Student Expert/Leader",
        "domain": "Tech",
        "keywords": ("student ambassador", "microsoft student ambassadors"),
    },
    IMAGINE_CUP_URL: {
        "name": "Microsoft Imagine Cup",
        "role_type": "Creator/Influencer",
        "domain": "Tech",
        "keywords": ("imagine cup",),
    },
    LEAP_URL: {
        "name": "Microsoft LEAP Apprenticeship Program",
        "role_type": "Other",
        "domain": "Tech",
        "keywords": ("leap", "apprenticeship"),
    },
}


class MicrosoftScraper(EnhancedBaseScraper):
    """Microsoft student programs scraper (hybrid: live fetch + parsed fields)."""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list[str]:
        return [MSA_URL, IMAGINE_CUP_URL, LEAP_URL]

    def parse_program_page(self, url: str) -> dict | None:
        config = PROGRAM_CONFIG.get(url)
        if not config:
            logger.warning("Unknown Microsoft program URL: %s", url)
            return None

        fetch_timeout = 60 if "imaginecup.microsoft.com" in url else 15
        soup = self._fetch_page(url, timeout=fetch_timeout)
        if not soup:
            return None

        text = page_text(soup)
        lower = text.lower()
        if not any(keyword in lower for keyword in config["keywords"]):
            logger.warning("Microsoft page missing expected signals for %s", config["name"])
            return None

        description = first_paragraph(soup) or config["name"]
        apply_url = url
        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text(strip=True).lower()
            if href.startswith("http") and "apply" in link_text:
                apply_url = href
                break

        return {
            "name": config["name"],
            "company": self.company_name,
            "apply_url": apply_url,
            "status": infer_status_from_text(text),
            "role_type": config["role_type"],
            "domain": config["domain"],
            "eligibility_summary": (
                "Students and early-career candidates (see program page for current requirements)"
            ),
            "location_notes": "Global / varies by program",
            "compensation_bucket": "Unpaid-or-perks",
            "last_verified": today_iso(),
            "short_description": description[:300],
            "source_url": url,
            "source_snippet": snippet_from_text(text),
            "school_restricted": False,
            "notes": f"Parsed from live Microsoft program page ({url}).",
        }
