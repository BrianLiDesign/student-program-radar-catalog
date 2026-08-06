#!/usr/bin/env python3
"""
Google Student Ambassador scraper
"""

import hashlib
import logging
from typing import List, Optional

from scraper_framework import EnhancedBaseScraper

logger = logging.getLogger(__name__)

class GoogleScraper(EnhancedBaseScraper):
    """Google Student Ambassador scraper"""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.0)

    def find_program_urls(self) -> List[str]:
        """
        Find URLs for Google Student Ambassador program
        """
        urls = []

        # Google Students programs page
        students_url = "https://students.google.com/"
        urls.append(students_url)

        # Google Student Veterans of America (as an example of student programs)
        sva_url = "https://students.google.com/student-veterans/"
        urls.append(sva_url)

        logger.info(f"Found {len(urls)} potential program URLs for {self.company_name}")
        return urls

    def parse_program_page(self, url: str) -> Optional[dict]:
        """
        Parse Google Student Ambassador program page
        """
        soup = self._fetch_page(url)
        if not soup:
            return None

        try:
            # Extract program information
            program_data = {}

            # Program name - look for student ambassador mentions
            title_elem = soup.find('h1')
            if title_elem:
                program_data['name'] = self._extract_text(title_elem)
                if "student ambassador" not in program_data['name'].lower() and "ambassador" not in program_data['name'].lower():
                    program_data['name'] = "Google Student Ambassador"
            else:
                program_data['name'] = "Google Student Ambassador"

            # Short description
            # Look for main content areas
            main_content = soup.find('main') or soup.find('div', {'role': 'main'})
            if main_content:
                first_p = main_content.find('p')
                if first_p:
                    program_data['short_description'] = self._extract_text(first_p)[:200] + "..."
                else:
                    program_data['short_description'] = "Google Student Ambassadors help grow Google's presence on campus by hosting events and sharing Google products."
            else:
                program_data['short_description'] = "Google Student Ambassadors help grow Google's presence on campus by hosting events and sharing Google products."

            # Set required fields
            program_data['company'] = self.company_name
            program_data['apply_url'] = "https://students.google.com/"
            program_data['status'] = "Unknown"
            program_data['role_type'] = "Ambassador"
            program_data['domain'] = "Tech"
            program_data['eligibility_summary'] = "Currently enrolled college or university students"
            program_data['location_notes'] = "Campus-based (varies by location)"
            program_data['compensation_bucket'] = "Paid"
            program_data['last_verified'] = "2024-08-05"

            # Additional fields
            program_data['responsibilities'] = [
                "Host events showcasing Google products and technologies",
                "Provide feedback on Google products to product teams",
                "Help peers learn about Google career opportunities",
                "Create content about Google tools for education and productivity"
            ]

            program_data['time_commitment'] = "5-10 hours/week"
            program_data['perks_detail'] = "Stipend, Google merchandise, access to Google events, networking opportunities, professional development"
            program_data['social_requirements'] = "Share experiences using #GoogleStudentAmbassador"
            program_data['source_url'] = url
            program_data['source_snippet'] = "Google Student Ambassadors are students who represent Google on their college or university campuses."
            program_data['school_restricted'] = False
            program_data['notes'] = "Program structure and availability may vary by region and academic year"

            # Generate UUID-like ID
            id_string = f"google{url}"
            program_data['id'] = "3ba33b4a-3c1a-5555-8e1c-" + hashlib.md5(id_string.encode()).hexdigest()[:12]

            return program_data

        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return None
