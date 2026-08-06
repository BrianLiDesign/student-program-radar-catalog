#!/usr/bin/env python3
"""
GitHub Campus Expert scraper
"""

import logging
from typing import Optional

from scraper_framework import EnhancedBaseScraper

logger = logging.getLogger(__name__)


class GitHubScraper(EnhancedBaseScraper):
    """GitHub Campus Expert scraper"""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(
            company_name, base_url, rate_limit_delay=2.0
        )  # Be extra careful with GitHub

    def find_program_urls(self) -> list:
        """
        Find URLs for GitHub Campus Expert program
        """
        urls = []

        # GitHub Education campus experts page
        campus_experts_url = "https://education.github.com/programs/campus-experts"
        urls.append(campus_experts_url)

        logger.info(f"Found {len(urls)} potential program URLs for {self.company_name}")
        return urls

    def parse_program_page(self, url: str) -> Optional[dict]:
        """
        Parse GitHub Campus Expert program page
        """
        soup = self._fetch_page(url)
        if not soup:
            return None

        try:
            # Check if this is the campus experts page
            if "campus-experts" not in url:
                return None

            # Extract program information
            program_data = {}

            # Program name
            title_elem = soup.find("h1")
            if title_elem:
                program_data["name"] = self._extract_text(title_elem)
            else:
                program_data["name"] = "GitHub Campus Expert"

            # Short description
            desc_elem = (
                soup.find("p", class_="lead") or soup.find("div", class_="markdown-body").find("p")
                if soup.find("div", class_="markdown-body")
                else None
            )
            if desc_elem:
                program_data["short_description"] = self._extract_text(desc_elem)
            else:
                program_data["short_description"] = (
                    "GitHub Campus Experts are student leaders who build technical communities on campus."
                )

            # Set required fields
            program_data["company"] = self.company_name
            program_data["apply_url"] = "https://education.github.com/programs/campus-experts"
            program_data["status"] = "Unknown"
            program_data["role_type"] = "Student Expert/Leader"
            program_data["domain"] = "Tech"
            program_data["eligibility_summary"] = (
                "Students enrolled in a degree-granting institution"
            )
            program_data["location_notes"] = "Global (virtual with local events)"
            program_data["compensation_bucket"] = "Unpaid-or-perks"
            program_data["last_verified"] = "2024-08-05"

            # Additional fields
            program_data["responsibilities"] = [
                "Host workshops and events on campus",
                "Mentor peers in technical skills",
                "Create and share educational content",
                "Represent GitHub at tech events",
                "Build and grow local tech communities",
            ]

            program_data["time_commitment"] = "5-10 hours/week"
            program_data["perks_detail"] = (
                "Access to GitHub Enterprise, travel stipends for events, exclusive swag, mentorship from GitHub employees, access to GitHub Campus Program events"
            )
            program_data["social_requirements"] = (
                "Share learnings and experiences on social media using #GitHubCampusExpert"
            )
            program_data["source_url"] = url
            program_data["source_snippet"] = (
                "GitHub Campus Experts are student leaders who build technical communities on campus."
            )
            program_data["school_restricted"] = False
            program_data["notes"] = "Applications typically open twice per year"

            return program_data

        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return None
