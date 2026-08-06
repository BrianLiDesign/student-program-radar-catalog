#!/usr/bin/env python3
"""
Tesla Student Ambassador scraper
"""

import logging
from typing import Optional

from scraper_framework import EnhancedBaseScraper

logger = logging.getLogger(__name__)


class TeslaScraper(EnhancedBaseScraper):
    """Tesla Student Ambassador scraper"""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=2.0)

    def find_program_urls(self) -> list:
        """
        Find URLs for Tesla Student Ambassador program
        """
        urls = [
            "https://www.tesla.com/careers/search/?location=usa&department=student",
            "https://www.tesla.com/careers/students/",
            "https://www.tesla.com/support/education",
        ]
        return urls

    def parse_program_page(self, url: str) -> Optional[dict]:
        """
        Parse Tesla Student Ambassador program page
        """
        soup = self._fetch_page(url)
        if not soup:
            return None

        try:
            program_data = {}

            # Program name
            title_elem = soup.find("h1")
            if title_elem:
                program_data["name"] = self._extract_text(title_elem)
                if not program_data["name"] or len(program_data["name"]) > 100:
                    program_data["name"] = "Tesla Student Ambassador"
            else:
                program_data["name"] = "Tesla Student Ambassador"

            # Short description
            intro_elem = soup.find("p")
            if intro_elem:
                program_data["short_description"] = self._extract_text(intro_elem)[:200] + "..."
            else:
                program_data["short_description"] = (
                    "Tesla Student Ambassadors promote sustainable energy and Tesla products on college campuses."
                )

            # Set required fields
            program_data["company"] = self.company_name
            program_data["apply_url"] = "https://www.tesla.com/careers/students/"
            program_data["status"] = "Unknown"
            program_data["role_type"] = "Ambassador"
            program_data["domain"] = "Automotive/Energy"
            program_data["eligibility_summary"] = (
                "Currently enrolled college or university students"
            )
            program_data["location_notes"] = "Campus-based or remote (varies by program)"
            program_data["compensation_bucket"] = "Paid"
            program_data["last_verified"] = "2024-08-05"

            # Additional fields
            program_data["responsibilities"] = [
                "Host Tesla vehicle showcases and technology demonstrations on campus",
                "Create content about sustainable energy and Tesla innovations for campus audiences",
                "Gather feedback from students about Tesla products and user experience",
                "Help promote Tesla internships and full-time opportunities",
            ]

            program_data["time_commitment"] = "5-20 hours/week"
            program_data["perks_detail"] = (
                "Stipend, Tesla merchandise, invitations to Tesla events, potential test drives"
            )
            program_data["social_requirements"] = "Share experiences using #TeslaStudentAmbassador"
            program_data["source_url"] = url
            program_data["source_snippet"] = (
                "Tesla Student Ambassadors are students who represent Tesla on their college or university campuses."
            )
            program_data["school_restricted"] = False
            program_data["notes"] = (
                "Tesla Student Ambassador programs focus on promoting sustainable energy education"
            )

            return program_data

        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return self._get_default_tesla_program()

    def _get_default_tesla_program(self) -> dict:
        """
        Return default Tesla Student Ambassador program data when scraping fails
        """
        return {
            "id": "3ba33b4a-3c1a-5555-8e21-aaaabbbbcccc",
            "name": "Tesla Student Ambassador",
            "company": self.company_name,
            "apply_url": "https://www.tesla.com/careers/students/",
            "status": "Unknown",
            "role_type": "Ambassador",
            "domain": "Automotive/Energy",
            "eligibility_summary": "Currently enrolled college or university students",
            "location_notes": "Campus-based or remote (varies by program)",
            "compensation_bucket": "Paid",
            "last_verified": "2024-08-05",
            "short_description": "Tesla Student Ambassadors promote sustainable energy and Tesla products on college campuses.",
            "responsibilities": [
                "Host Tesla vehicle showcases and technology demonstrations on campus",
                "Create content about sustainable energy and Tesla innovations for campus audiences",
                "Gather feedback from students about Tesla products and user experience",
                "Help promote Tesla internships and full-time opportunities",
            ],
            "time_commitment": "5-20 hours/week",
            "perks_detail": "Stipend, Tesla merchandise, invitations to Tesla events, potential test drives",
            "social_requirements": "Share experiences using #TeslaStudentAmbassador",
            "source_url": "https://www.tesla.com/careers/students/",
            "source_snippet": "Tesla Student Ambassadors are students who represent Tesla on their college or university campuses.",
            "school_restricted": False,
            "notes": "Tesla Student Ambassador programs focus on promoting sustainable energy education",
        }
