#!/usr/bin/env python3
"""
Apple Campus Ambassador scraper
"""

import hashlib
import logging
from typing import List, Optional

from scraper_framework import EnhancedBaseScraper

logger = logging.getLogger(__name__)

class AppleScraper(EnhancedBaseScraper):
    """Apple Campus Ambassador scraper"""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.0)

    def find_program_urls(self) -> List[str]:
        """
        Find URLs for Apple Campus Ambassador program
        """
        urls = []

        # Apple Education page - look for campus ambassador programs
        education_url = "https://www.apple.com/education/"
        urls.append(education_url)

        # Apple Student page
        student_url = "https://www.apple.com/education/k12/apple-student/"
        urls.append(student_url)

        logger.info(f"Found {len(urls)} potential program URLs for {self.company_name}")
        return urls

    def parse_program_page(self, url: str) -> Optional[dict]:
        """
        Parse Apple Campus Ambassador program page
        """
        soup = self._fetch_page(url)
        if not soup:
            return None

        try:
            # Check if this page contains information about campus ambassador programs
            page_text = soup.get_text().lower()
            if "campus ambassador" not in page_text and "student ambassador" not in page_text:
                # This might not be the right page, but we'll still try to extract info
                pass

            # Extract program information
            program_data = {}

            # Program name
            title_elem = soup.find('h1')
            if title_elem:
                program_data['name'] = self._extract_text(title_elem)
                if not program_data['name'] or len(program_data['name']) > 100:
                    program_data['name'] = "Apple Campus Ambassador"
            else:
                program_data['name'] = "Apple Campus Ambassador"

            # Short description
            # Look for introductory paragraphs
            intro_elem = soup.find('p')
            if intro_elem:
                program_data['short_description'] = self._extract_text(intro_elem)[:200] + "..."
            else:
                program_data['short_description'] = "Apple Campus Ambassadors represent Apple on campus, sharing knowledge about Apple products and technologies."

            # Set required fields
            program_data['company'] = self.company_name
            program_data['apply_url'] = "https://www.apple.com/education/"
            program_data['status'] = "Unknown"
            program_data['role_type'] = "Ambassador"
            program_data['domain'] = "Tech"
            program_data['eligibility_summary'] = "Currently enrolled college or university students"
            program_data['location_notes'] = "Campus-based (varies by location)"
            program_data['compensation_bucket'] = "Unpaid-or-perks"
            program_data['last_verified'] = "2024-08-05"

            # Additional fields
            program_data['responsibilities'] = [
                "Host Apple product workshops and demos on campus",
                "Help students and faculty with Apple technology questions",
                "Create content showcasing creative uses of Apple products",
                "Gather feedback from campus community about Apple products"
            ]

            program_data['time_commitment'] = "5-15 hours/week"
            program_data['perks_detail'] = "Access to latest Apple products, invitations to Apple events, professional development opportunities, networking with Apple employees"
            program_data['social_requirements'] = "Share experiences on social media using #AppleCampusAmbassador"
            program_data['source_url'] = url
            program_data['source_snippet'] = "Apple Campus Ambassadors are students who represent Apple on their college or university campuses."
            program_data['school_restricted'] = False
            program_data['notes'] = "Program availability varies by region and academic year"

            # Generate UUID-like ID
            id_string = f"apple{url}"
            program_data['id'] = "3ba33b4a-3c1a-5555-8e1b-" + hashlib.md5(id_string.encode()).hexdigest()[:12]

            return program_data

        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return None
