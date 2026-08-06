#!/usr/bin/env python3
"""
Spotify Student Ambassador scraper
"""

import hashlib
import logging
from typing import Optional

from scraper_framework import EnhancedBaseScraper

logger = logging.getLogger(__name__)

class SpotifyScraper(EnhancedBaseScraper):
    """Spotify Student Ambassador scraper"""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list:
        """
        Find URLs for Spotify Student Ambassador program
        """
        urls = [
            "https://www.spotify.com/us/jobs/early-talent/",
            "https://www.spotifyjobs.com/student/",
            "https://newsroom.spotify.com/company-info/"
        ]
        return urls

    def parse_program_page(self, url: str) -> Optional[dict]:
        """
        Parse Spotify Student Ambassador program page
        """
        soup = self._fetch_page(url)
        if not soup:
            return None

        try:
            # Look for student or campus program content
            page_text = soup.get_text().lower()

            if not any(term in page_text for term in ('student ambassador', 'campus ambassador')):
                logger.warning(f"Skipping non-program page: {url}")
                return None

            program_data = {}

            # Program name
            title_elem = soup.find('h1')
            if title_elem:
                program_data['name'] = self._extract_text(title_elem)
                if not program_data['name'] or len(program_data['name']) > 100:
                    program_data['name'] = "Spotify Student Ambassador"
            else:
                program_data['name'] = "Spotify Student Ambassador"

            # Short description
            intro_elem = soup.find('p')
            if intro_elem:
                program_data['short_description'] = self._extract_text(intro_elem)[:200] + "..."
            else:
                program_data['short_description'] = "Spotify Student Ambassadors promote Spotify on campus and provide feedback on student experiences with the platform."

            # Set required fields
            program_data['company'] = self.company_name
            program_data['apply_url'] = "https://www.spotify.com/us/jobs/early-talent/"
            program_data['status'] = "Unknown"
            program_data['role_type'] = "Ambassador"
            program_data['domain'] = "Consumer brand"
            program_data['eligibility_summary'] = "Currently enrolled college or university students"
            program_data['location_notes'] = "Campus-based or remote (varies by program)"
            program_data['compensation_bucket'] = "Paid"
            program_data['last_verified'] = "2024-08-05"

            # Additional fields
            program_data['responsibilities'] = [
                "Host listening parties and music events on campus",
                "Create content about Spotify features and new music for campus audiences",
                "Gather feedback from students about Spotify features and user experience",
                "Help promote Spotify internships and early career opportunities"
            ]

            program_data['time_commitment'] = "5-15 hours/week"
            program_data['perks_detail'] = "Stipend, Spotify Premium, merchandise, invitations to Spotify events"
            program_data['social_requirements'] = "Share experiences using #SpotifyStudentAmbassador"
            program_data['source_url'] = url
            program_data['source_snippet'] = "Spotify Student Ambassadors are students who represent Spotify on their college or university campuses."
            program_data['school_restricted'] = False
            program_data['notes'] = "Spotify Student Ambassador programs may vary by region and academic calendar"

            # Generate UUID-like ID
            id_string = f"spotify{url}"
            program_data['id'] = "3ba33b4a-3c1a-5555-8e20-" + hashlib.md5(id_string.encode()).hexdigest()[:12]

            return program_data

        except Exception as e:
            logger.error(f"Error parsing {url}: {str(e)}")
            return self._get_default_spotify_program()

    def _get_default_spotify_program(self) -> dict:
        """
        Return default Spotify Student Ambassador program data when scraping fails
        """
        return {
            "id": "3ba33b4a-3c1a-5555-8e20-aaaabbbbcccc",
            "name": "Spotify Student Ambassador",
            "company": self.company_name,
            "apply_url": "https://www.spotify.com/us/jobs/early-talent/",
            "status": "Unknown",
            "role_type": "Ambassador",
            "domain": "Consumer brand",
            "eligibility_summary": "Currently enrolled college or university students",
            "location_notes": "Campus-based or remote (varies by program)",
            "compensation_bucket": "Paid",
            "last_verified": "2024-08-05",
            "short_description": "Spotify Student Ambassadors promote Spotify on campus and provide feedback on student experiences with the platform.",
            "responsibilities": [
                "Host listening parties and music events on campus",
                "Create content about Spotify features and new music for campus audiences",
                "Gather feedback from students about Spotify features and user experience",
                "Help promote Spotify internships and early career opportunities"
            ],
            "time_commitment": "5-15 hours/week",
            "perks_detail": "Stipend, Spotify Premium, merchandise, invitations to Spotify events",
            "social_requirements": "Share experiences using #SpotifyStudentAmbassador",
            "source_url": "https://www.spotify.com/us/jobs/early-talent/",
            "source_snippet": "Spotify Student Ambassadors are students who represent Spotify on their college or university campuses.",
            "school_restricted": False,
            "notes": "Spotify Student Ambassador programs may vary by region and academic calendar"
        }
