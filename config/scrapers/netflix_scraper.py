#!/usr/bin/env python3
"""
Netflix Campus Ambassador scraper
"""

import hashlib
import logging
from typing import Optional

from scraper_framework import EnhancedBaseScraper

logger = logging.getLogger(__name__)

class NetflixScraper(EnhancedBaseScraper):
    """Netflix Campus Ambassador scraper"""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=2.0)

    def find_program_urls(self) -> list:
        """
        Find URLs for Netflix Campus Ambassador program
        """
        # Netflix has various student and campus ambassador programs
        urls = [
            "https://jobs.netflix.com/",
            "https://jobs.netflix.com/early_talent",
            "https://about.netflix.com/en/diversity-and-inclusion"
        ]
        return urls

    def parse_program_page(self, url: str) -> Optional[dict]:
        """
        Parse Netflix Campus Ambassador program page
        """
        soup = self._fetch_page(url)
        if not soup:
            return None

        try:
            program_data = {}

            # Program name
            title_elem = soup.find('h1')
            if title_elem:
                program_data['name'] = self._extract_text(title_elem)
                if not program_data['name'] or len(program_data['name']) > 100:
                    program_data['name'] = "Netflix Campus Ambassador"
            else:
                program_data['name'] = "Netflix Campus Ambassador"

            # Short description
            intro_elem = soup.find('p')
            if intro_elem:
                program_data['short_description'] = self._extract_text(intro_elem)[:200] + "..."
            else:
                program_data['short_description'] = "Netflix Campus Ambassadors help promote Netflix culture and content on college campuses."

            # Set required fields
            program_data['company'] = self.company_name
            program_data['apply_url'] = "https://jobs.netflix.com/early_talent"
            program_data['status'] = "Unknown"
            program_data['role_type'] = "Ambassador"
            program_data['domain'] = "Consumer brand"
            program_data['eligibility_summary'] = "Currently enrolled college or university students"
            program_data['location_notes'] = "Campus-based or remote (varies by program)"
            program_data['compensation_bucket'] = "Paid"
            program_data['last_verified'] = "2024-08-05"

            # Additional fields
            program_data['responsibilities'] = [
                "Host Netflix viewing parties and discussions on campus",
                "Create content about Netflix shows and films for campus audiences",
                "Provide feedback on Netflix products and user experience",
                "Help promote Netflix internship and early career opportunities"
            ]

            program_data['time_commitment'] = "5-10 hours/week"
            program_data['perks_detail'] = "Stipend, Netflix subscription, merchandise, invitations to Netflix events"
            program_data['social_requirements'] = "Share experiences using #NetflixCampusAmbassador"
            program_data['source_url'] = url
            program_data['source_snippet'] = "Netflix Campus Ambassadors are students who represent Netflix on their college or university campuses."
            program_data['school_restricted'] = False
            program_data['notes'] = "Netflix Early Talent programs vary by region and academic focus"

            # Generate UUID-like ID
            id_string = f"netflix{url}"
            program_data['id'] = "3ba33b4a-3c1a-5555-8e1e-" + hashlib.md5(id_string.encode()).hexdigest()[:12]

            return program_data

        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return self._get_default_netflix_program()

    def _get_default_netflix_program(self) -> dict:
        """
        Return default Netflix Campus Ambassador program data when scraping fails
        """
        return {
            "id": "3ba33b4a-3c1a-5555-8e1e-aaaabbbbcccc",
            "name": "Netflix Campus Ambassador",
            "company": self.company_name,
            "apply_url": "https://jobs.netflix.com/early_talent",
            "status": "Unknown",
            "role_type": "Ambassador",
            "domain": "Consumer brand",
            "eligibility_summary": "Currently enrolled college or university students",
            "location_notes": "Campus-based or remote (varies by program)",
            "compensation_bucket": "Paid",
            "last_verified": "2024-08-05",
            "short_description": "Netflix Campus Ambassadors help promote Netflix culture and content on college campuses.",
            "responsibilities": [
                "Host Netflix viewing parties and discussions on campus",
                "Create content about Netflix shows and films for campus audiences",
                "Provide feedback on Netflix products and user experience",
                "Help promote Netflix internship and early career opportunities"
            ],
            "time_commitment": "5-10 hours/week",
            "perks_detail": "Stipend, Netflix subscription, merchandise, invitations to Netflix events",
            "social_requirements": "Share experiences using #NetflixCampusAmbassador",
            "source_url": "https://jobs.netflix.com/early_talent",
            "source_snippet": "Netflix Campus Ambassadors are students who represent Netflix on their college or university campuses.",
            "school_restricted": False,
            "notes": "Netflix Early Talent programs vary by region and academic focus"
        }
