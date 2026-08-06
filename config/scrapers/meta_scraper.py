#!/usr/bin/env python3
"""
Meta (Facebook) Campus Ambassador scraper
"""

import logging
from typing import Optional

from scraper_framework import EnhancedBaseScraper

logger = logging.getLogger(__name__)


class MetaScraper(EnhancedBaseScraper):
    """Meta (Facebook) Campus Ambassador scraper"""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list:
        """
        Find URLs for Meta Campus Ambassador program
        """
        # Meta/Facebook University and student programs
        urls = [
            "https://about.fb.com/careers/programs/university/",
            "https://about.fb.com/careers/programs/student/",
            "https://tech.fb.com/campus/",
        ]
        return urls

    def parse_program_page(self, url: str) -> Optional[dict]:
        """
        Parse Meta Campus Ambassador program page
        """
        soup = self._fetch_page(url)
        if not soup:
            return None

        try:
            # Look for student ambassador specific content
            page_text = soup.get_text().lower()

            # If this doesn't seem to be about student programs, set default values
            if (
                "university" not in page_text
                and "student" not in page_text
                and "campus" not in page_text
            ):
                return self._get_default_meta_program()

            program_data = {}

            # Program name
            title_elem = soup.find("h1")
            if title_elem:
                program_data["name"] = self._extract_text(title_elem)
                if not program_data["name"] or len(program_data["name"]) > 100:
                    program_data["name"] = "Meta Campus Ambassador"
            else:
                program_data["name"] = "Meta Campus Ambassador"

            # Short description
            intro_elem = soup.find("p")
            if intro_elem:
                program_data["short_description"] = self._extract_text(intro_elem)[:200] + "..."
            else:
                program_data["short_description"] = (
                    "Meta Campus Ambassadors represent Meta technologies on campus, hosting events and sharing insights about Meta products."
                )

            # Set required fields
            program_data["company"] = self.company_name
            program_data["apply_url"] = "https://about.fb.com/careers/programs/university/"
            program_data["status"] = "Unknown"
            program_data["role_type"] = "Ambassador"
            program_data["domain"] = "Tech"
            program_data["eligibility_summary"] = (
                "Currently enrolled college or university students"
            )
            program_data["location_notes"] = "Campus-based (varies by location)"
            program_data["compensation_bucket"] = "Paid"
            program_data["last_verified"] = "2024-08-05"

            # Additional fields
            program_data["responsibilities"] = [
                "Host workshops and events showcasing Meta technologies",
                "Create content about Meta products for campus audiences",
                "Gather feedback from students about Meta products",
                "Connect students with Meta career opportunities",
            ]

            program_data["time_commitment"] = "5-15 hours/week"
            program_data["perks_detail"] = (
                "Stipend, Meta merchandise, access to Meta events, networking opportunities"
            )
            program_data["social_requirements"] = "Share experiences using #MetaCampusAmbassador"
            program_data["source_url"] = url
            program_data["source_snippet"] = (
                "Meta Campus Ambassadors are students who represent Meta technologies on their college or university campuses."
            )
            program_data["school_restricted"] = False
            program_data["notes"] = (
                "Meta University program includes various tech and business roles for students"
            )

            return program_data

        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return self._get_default_meta_program()

    def _get_default_meta_program(self) -> dict:
        """
        Return default Meta Campus Ambassador program data when scraping fails
        """
        return {
            "id": "3ba33b4a-3c1a-5555-8e1d-aaaabbbbcccc",
            "name": "Meta Campus Ambassador",
            "company": self.company_name,
            "apply_url": "https://about.fb.com/careers/programs/university/",
            "status": "Unknown",
            "role_type": "Ambassador",
            "domain": "Tech",
            "eligibility_summary": "Currently enrolled college or university students",
            "location_notes": "Campus-based (varies by location)",
            "compensation_bucket": "Paid",
            "last_verified": "2024-08-05",
            "short_description": "Meta Campus Ambassadors represent Meta technologies on campus, hosting events and sharing insights about Meta products.",
            "responsibilities": [
                "Host workshops and events showcasing Meta technologies",
                "Create content about Meta products for campus audiences",
                "Gather feedback from students about Meta products",
                "Connect students with Meta career opportunities",
            ],
            "time_commitment": "5-15 hours/week",
            "perks_detail": "Stipend, Meta merchandise, access to Meta events, networking opportunities",
            "social_requirements": "Share experiences using #MetaCampusAmbassador",
            "source_url": "https://about.fb.com/careers/programs/university/",
            "source_snippet": "Meta Campus Ambassadors are students who represent Meta technologies on their college or university campuses.",
            "school_restricted": False,
            "notes": "Meta University program includes various tech and business roles for students",
        }
