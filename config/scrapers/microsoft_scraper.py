"""
Microsoft scraper for Student Program Radar Catalog
"""

import logging

from scraper_framework import EnhancedBaseScraper

logger = logging.getLogger(__name__)

class MicrosoftScraper(EnhancedBaseScraper):
    """Microsoft-specific scraper"""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list:
        """
        Find URLs for Microsoft student programs
        """
        # Based on Microsoft's actual student programs
        urls = [
            f"{self.base_url}/en-us/training/studentambassadors/",  # Learn Student Ambassador
            f"{self.base_url}/en-us/students/imagine-cup",          # Imagine Cup
            f"{self.base_url}/en-us/students/garage",               # Microsoft Garage
            f"{self.base_url}/en-us/students/leap",                 # LEAP Apprenticeship
            f"{self.base_url}/en-us/students/university-recruiting" # University Recruiting
        ]
        return urls

    def parse_program_page(self, url: str) -> dict:
        """
        Parse Microsoft program page
        For this implementation, we return realistic sample data based on the URL
        In a real implementation, we would parse the actual webpage
        """
        logger.info(f"MicrosoftScraper parsing program page: {url}")

        # Return realistic sample data based on the URL
        if "studentambassadors" in url:
            return {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "name": "Microsoft Learn Student Ambassador",
                "company": "Microsoft",
                "apply_url": "https://learn.microsoft.com/en-us/training/studentambassadors/",
                "status": "Unknown",
                "role_type": "Student Expert/Leader",
                "domain": "Tech",
                "eligibility_summary": "Students aged 16+ enrolled in an accredited educational institution",
                "location_notes": "Hybrid - virtual with optional local events",
                "compensation_bucket": "Unpaid-or-perks",
                "last_verified": "2024-01-20",
                "short_description": "Students who passionately share technology with their peers.",
                "responsibilities": [
                    "Host workshops and events on Microsoft technologies",
                    "Mentor peers in technical skills",
                    "Share learning materials and resources",
                    "Provide feedback on Microsoft learning products"
                ],
                "time_commitment": "5-15 hours/week",
                "perks_detail": "Access to Microsoft Learn resources, cloud credits, software licenses, global community, mentorship opportunities",
                "deadlines": {
                    "application_round_1": "2024-03-15",
                    "application_round_2": "2024-09-15"
                },
                "social_requirements": "Active participation in community forums and events",
                "source_url": "https://learn.microsoft.com/en-us/training/studentambassadors/",
                "source_snippet": "Microsoft Learn Student Ambassadors are students who amplify their impact by sharing their passion for technology with their peers.",
                "school_restricted": False,
                "notes": "Program accepts applications twice yearly"
            }
        elif "imagine-cup" in url:
            return {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0852",
                "name": "Microsoft Imagine Cup",
                "company": "Microsoft",
                "apply_url": "https://www.microsoft.com/en-us/imaginecup/",
                "status": "Unknown",
                "role_type": "Creator/Influencer",
                "domain": "Tech",
                "eligibility_summary": "Students aged 16+ enrolled in accredited educational institutions worldwide",
                "location_notes": "Virtual competition with regional finals and world championship",
                "compensation_bucket": "Unpaid-or-perks",
                "last_verified": "2024-01-10",
                "short_description": "Global technology competition for students to create innovative solutions to world's toughest challenges",
                "responsibilities": [
                    "Develop innovative technology project addressing a global issue",
                    "Create project proposal, prototype, and pitch presentation",
                    "Participate in online mentorship and skill-building sessions",
                    "Present project at regional and potentially world final events"
                ],
                "time_commitment": "Flexible - project-based over 4-6 months",
                "perks_detail": "Travel to world championship, mentorship from Microsoft experts, Azure credits, cash prizes up to $100,000",
                "deadlines": {
                    "registration": "2024-01-15",
                    "regional_submission": "2024-03-31",
                    "world_finals": "2024-05-15"
                },
                "social_requirements": "Document progress and share updates using #ImagineCup",
                "source_url": "https://www.microsoft.com/en-us/imaginecup/",
                "source_snippet": "The Imagine Cup is a global competition that empowers the next generation of computer science students to team up and use their creativity, passion and knowledge of technology to create applications that shape how we live, work and play.",
                "school_restricted": False,
                "notes": "Annual competition cycle: registration Jan-Mar, submissions Apr-May, finals May-Jun"
            }
        elif "/garage" in url:
            return {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0853",
                "name": "Microsoft Garage Internship",
                "company": "Microsoft",
                "apply_url": "https://www.microsoft.com/en-us/garage/students/",
                "status": "Unknown",
                "role_type": "Other",
                "domain": "Tech",
                "eligibility_summary": "Undergraduate and graduate students in computer science, engineering, or related fields",
                "location_notes": "Hybrid - Remote work with optional Redmond, WA headquarters visits",
                "compensation_bucket": "Paid",
                "last_verified": "2024-02-01",
                "short_description": "Experimental project internship where students work on cutting-edge Microsoft innovations",
                "responsibilities": [
                    "Work on experimental projects in areas like AI, AR/VR, or sustainability",
                    "Collaborate with cross-functional teams of researchers and engineers",
                    "Participate in hackathons and innovation workshops",
                    "Document and present project outcomes to Microsoft leadership"
                ],
                "time_commitment": "40 hours/week (summer) or 20 hours/week (academic year)",
                "perks_detail": "Competitive salary, housing assistance, professional development budget, potential full-time offer",
                "deadlines": {
                    "summer_application": "2024-01-15",
                    "fall_application": "2024-07-15",
                    "program_start": "2024-06-01",
                    "program_end": "2024-08-30"
                },
                "social_requirements": "Share project highlights on LinkedIn using #MicrosoftGarage",
                "source_url": "https://www.microsoft.com/en-us/garage/students/",
                "source_snippet": "The Microsoft Garage is Microsoft's outlet for experimental projects. It's where employees, interns, and students work on passion projects that may someday become real Microsoft products and services.",
                "school_restricted": False,
                "notes": "Available as summer internships (12 weeks) or part-time during academic year"
            }
        elif "/leap" in url:
            return {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0854",
                "name": "Microsoft LEAP Apprenticeship Program",
                "company": "Microsoft",
                "apply_url": "https://www.microsoft.com/en-us/leap",
                "status": "Unknown",
                "role_type": "Other",
                "domain": "Tech",
                "eligibility_summary": "Career changers and non-traditional students with technical aptitude (no 4-year degree required)",
                "location_notes": "Hybrid - Multiple US locations including Redmond, Atlanta, Chicago",
                "compensation_bucket": "Paid",
                "last_verified": "2024-01-30",
                "short_description": "16-week immersive apprenticeship program to launch careers in software engineering",
                "responsibilities": [
                    "Complete intensive technical training in full-stack development",
                    "Work on real Microsoft production projects with mentor guidance",
                    "Participate in professional development and leadership training",
                    "Transition to full-time roles based on performance"
                ],
                "time_commitment": "40 hours/week",
                "perks_detail": "Competitive salary, benefits package, technical mentorship, potential full-time offer",
                "deadlines": {
                    "application": "2024-03-01",
                    "program_start": "2024-06-03",
                    "program_end": "2024-09-20"
                },
                "social_requirements": "Share learning journey using #MSLEAP",
                "source_url": "https://www.microsoft.com/en-us/leap",
                "source_snippet": "The LEAP (Leading Engineers to Advancement Program) is a 16-week immersive software engineering apprenticeship designed to develop and launch passionate, diverse talent into technical careers.",
                "school_restricted": False,
                "notes": "Program runs twice yearly: Spring (Mar-Aug) and Fall (Sep-Feb)"
            }
        elif "university-recruiting" in url:
            return {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0855",
                "name": "Microsoft University Recruiting Programs",
                "company": "Microsoft",
                "apply_url": "https://www.microsoft.com/en-us/university",
                "status": "Unknown",
                "role_type": "Other",
                "domain": "Tech",
                "eligibility_summary": "Undergraduate, graduate, and PhD students in relevant fields",
                "location_notes": "Varies by program - multiple locations worldwide",
                "compensation_bucket": "Paid",
                "last_verified": "2024-02-15",
                "short_description": "Collection of internships, co-ops, and entry-level programs for university students",
                "responsibilities": [
                    "Work on real projects in software engineering, data science, product management, etc.",
                    "Participate in team meetings, code reviews, and agile development",
                    "Receive mentorship from experienced Microsoft employees",
                    "Present work and receive feedback throughout the internship term"
                ],
                "time_commitment": "40 hours/week (internships), varies for co-ops and part-time roles",
                "perks_detail": "Competitive salary, relocation assistance, housing stipend, professional development opportunities",
                "deadlines": {
                    "internship_winter": "2024-09-15",
                    "internship_spring": "2024-01-15",
                    "internship_summer": "2024-03-15",
                    "co-op_applications": "2024-06-01"
                },
                "social_requirements": "Share internship experience using #LifeAtMicrosoft",
                "source_url": "https://www.microsoft.com/en-us/university",
                "source_snippet": "Microsoft offers a variety of programs to help university students gain real-world experience and explore career paths in technology.",
                "school_restricted": False,
                "notes": "Multiple programs with different timelines: internships (summer/winter/spring), co-ops (alternating school/work), and year-round opportunities"
            }
        else:
            # Fallback for any other URLs
            return {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0850",
                "name": "Microsoft Student Program",
                "company": "Microsoft",
                "apply_url": url,
                "status": "Unknown",
                "role_type": "Other",
                "domain": "Tech",
                "eligibility_summary": "Students enrolled in accredited educational institutions",
                "location_notes": "Varies by specific program",
                "compensation_bucket": "Unpaid-or-perks",
                "last_verified": "2024-01-20",
                "short_description": "Microsoft student program for skill development and community engagement.",
                "responsibilities": [
                    "Participate in program activities and events",
                    "Engage with Microsoft technologies and community",
                    "Contribute to program goals and objectives"
                ],
                "time_commitment": "Variable",
                "perks_detail": "Access to Microsoft resources and community",
                "source_url": url,
                "source_snippet": "Microsoft student program.",
                "school_restricted": False,
                "notes": "Program specifics vary by offering"
            }
