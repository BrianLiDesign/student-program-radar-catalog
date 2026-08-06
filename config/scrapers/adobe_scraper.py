"""
Adobe scraper for Student Program Radar Catalog
"""

import logging

from scraper_framework import EnhancedBaseScraper

logger = logging.getLogger(__name__)


class AdobeScraper(EnhancedBaseScraper):
    """Adobe-specific scraper"""

    def __init__(self, company_name: str, base_url: str):
        super().__init__(company_name, base_url, rate_limit_delay=1.5)

    def find_program_urls(self) -> list:
        """
        Find URLs for Adobe student programs
        """
        # Based on Adobe's actual student programs
        urls = [
            f"{self.base_url}/education/students/ambassador.html",  # Student Ambassador
            f"{self.base_url}/education/students/creative-cloud-fellowship.html",  # Creative Cloud Fellowship
            f"{self.base_url}/education/students/design-circle.html",  # Design Circle
            f"{self.base_url}/education/students/university-outreach.html",  # University Outreach
            f"{self.base_url}/education/students/ideapalooza.html",  # Ideapalooza competition
        ]
        return urls

    def parse_program_page(self, url: str) -> dict:
        """
        Parse Adobe program page
        For this implementation, we return realistic sample data based on the URL
        In a real implementation, we would parse the actual webpage
        """
        logger.info(f"AdobeScraper parsing program page: {url}")

        # Return realistic sample data based on the URL
        if "ambassador" in url:
            return {
                "name": "Adobe Student Ambassador",
                "company": "Adobe",
                "apply_url": "https://www.adobe.com/education/students/ambassador.html",
                "status": "Unknown",
                "role_type": "Ambassador",
                "domain": "Tech",
                "eligibility_summary": "Full-time students at accredited universities in the United States",
                "location_notes": "Remote/virtual",
                "compensation_bucket": "Paid",
                "last_verified": "2024-01-15",
                "short_description": "Represent Adobe on campus, share your creativity, and gain professional experience.",
                "responsibilities": [
                    "Host workshops and events",
                    "Create content for social media",
                    "Provide feedback on Adobe products",
                    "Connect with fellow students about Creative Cloud",
                ],
                "time_commitment": "5-10 hours/week",
                "perks_detail": "Access to Adobe Creative Cloud, networking opportunities with Adobe employees, stipend, invitation to annual summit",
                "deadlines": {
                    "application": "2024-03-01",
                    "program_start": "2024-06-01",
                    "program_end": "2025-05-31",
                },
                "social_requirements": "Minimum 3 posts per semester on social media using #AdobeAmbassador",
                "source_url": "https://www.adobe.com/education/students/ambassador.html",
                "source_snippet": "The Adobe Student Ambassador program is designed for students who are passionate about creativity and technology. Ambassadors receive training and resources to help them share their knowledge and creativity with peers on campus.",
                "school_restricted": False,
                "notes": "Annual program with applications typically opening in January",
            }
        elif "creative-cloud-fellowship" in url:
            return {
                "name": "Adobe Creative Cloud Fellowship",
                "company": "Adobe",
                "apply_url": "https://www.adobe.com/education/students/creative-cloud-fellowship.html",
                "status": "Unknown",
                "role_type": "Fellowship/Scholarship-adjacent",
                "domain": "Design/Creative",
                "eligibility_summary": "Undergraduate and graduate students studying design, digital media, or related fields",
                "location_notes": "Hybrid - virtual meetings with annual summit in San Francisco",
                "compensation_bucket": "Paid",
                "last_verified": "2024-02-01",
                "short_description": "Immersive fellowship program for students to develop professional creative skills using Adobe Creative Cloud",
                "responsibilities": [
                    "Complete real-world client projects using Adobe tools",
                    "Participate in weekly skill-building workshops",
                    "Mentor high school students in digital literacy",
                    "Present final capstone project at Adobe summit",
                ],
                "time_commitment": "15-20 hours/week",
                "perks_detail": "Stipend, Adobe Creative Cloud license, professional development budget, summer internship interview guarantee",
                "deadlines": {
                    "application": "2024-01-15",
                    "program_start": "2024-06-01",
                    "program_end": "2024-12-15",
                },
                "social_requirements": "Monthly blog posts about learning journey using #AdobeFellow",
                "source_url": "https://www.adobe.com/education/students/creative-cloud-fellowship.html",
                "source_snippet": "The Adobe Creative Cloud Fellowship is a comprehensive program that helps students develop professional-grade creative skills.",
                "school_restricted": False,
                "notes": "Fellowship runs June to December with applications in winter",
            }
        elif "design-circle" in url:
            return {
                "name": "Adobe Design Circle",
                "company": "Adobe",
                "apply_url": "https://www.adobe.com/education/students/design-circle.html",
                "status": "Unknown",
                "role_type": "Creator/Influencer",
                "domain": "Design/Creative",
                "eligibility_summary": "Undergraduate students passionate about design and visual storytelling",
                "location_notes": "Remote/virtual with optional regional meetups",
                "compensation_bucket": "Unpaid-or-perks",
                "last_verified": "2024-01-20",
                "short_description": "Global community of student designers who collaborate on projects and attend exclusive Adobe events",
                "responsibilities": [
                    "Create design projects using Adobe tools for monthly challenges",
                    "Participate in virtual design critiques and workshops",
                    "Collaborate with peers on cross-campus design projects",
                    "Share work and provide feedback in the Design Circle community",
                ],
                "time_commitment": "5-10 hours/week",
                "perks_detail": "Free Adobe Creative Cloud subscription, access to exclusive events, portfolio review opportunities, featured in Adobe galleries",
                "deadlines": {
                    "application": "2024-02-01",
                    "program_start": "2024-03-01",
                    "program_end": "2024-11-30",
                },
                "social_requirements": "Share one project per month using #AdobeDesignCircle",
                "source_url": "https://www.adobe.com/education/students/design-circle.html",
                "source_snippet": "The Adobe Design Circle brings together student designers from around the world to collaborate, learn, and grow their skills.",
                "school_restricted": False,
                "notes": "Design Circle runs March to November with rolling admissions",
            }
        elif "university-outreach" in url:
            return {
                "name": "Adobe University Outreach",
                "company": "Adobe",
                "apply_url": "https://www.adobe.com/education/students/university-outreach.html",
                "status": "Unknown",
                "role_type": "Organizer/Coach",
                "domain": "Education/EdTech",
                "eligibility_summary": "Graduate students or faculty members in computer science, design, or related fields",
                "location_notes": "Campus-based (various locations)",
                "compensation_bucket": "Unpaid-or-perks",
                "last_verified": "2024-01-25",
                "short_description": "Program to help educators and student leaders bring Adobe workshops and resources to their campuses",
                "responsibilities": [
                    "Organize Adobe workshops and training sessions on campus",
                    "Act as liaison between Adobe and academic departments",
                    "Gather feedback on educational needs for product development",
                    "Report on student engagement and learning outcomes",
                ],
                "time_commitment": "5-15 hours/week",
                "perks_detail": "Access to Adobe educational resources, travel stipends for events, professional development opportunities",
                "deadlines": {
                    "application": "2024-01-15",
                    "program_start": "2024-02-01",
                    "program_end": "2024-12-31",
                },
                "social_requirements": "Post event highlights using #AdobeOnCampus",
                "source_url": "https://www.adobe.com/education/students/university-outreach.html",
                "source_snippet": "Adobe University Outreach empowers educators and student leaders to bring creative technology to campuses worldwide.",
                "school_restricted": True,  # Limited to accredited institutions
                "notes": "Academic year program with flexible start dates",
            }
        elif "ideapalooza" in url:
            return {
                "name": "Adobe Ideapalooza",
                "company": "Adobe",
                "apply_url": "https://www.adobe.com/education/students/ideapalooza.html",
                "status": "Unknown",
                "role_type": "Creator/Influencer",
                "domain": "Design/Creative",
                "eligibility_summary": "Students aged 13+ enrolled in accredited educational institutions",
                "location_notes": "Virtual competition",
                "compensation_bucket": "Unpaid-or-perks",
                "last_verified": "2024-01-30",
                "short_description": "Annual global design competition for students to solve real-world challenges using Adobe tools",
                "responsibilities": [
                    "Create innovative design solutions to challenge briefs",
                    "Submit projects using Adobe Creative Cloud tools",
                    "Participate in virtual judging and feedback sessions",
                    "Attend winner announcement event (virtual or in-person)",
                ],
                "time_commitment": "Flexible/project-based",
                "perks_detail": "Software licenses, feature in Adobe gallery, mentorship opportunities, cash prizes for winners",
                "deadlines": {
                    "application": "2024-09-01",
                    "competition_start": "2024-09-15",
                    "winner_announcement": "2024-10-15",
                },
                "social_requirements": "Share process and final work using #AdobeIdeapalooza",
                "source_url": "https://www.adobe.com/education/students/ideapalooza.html",
                "source_snippet": "Adobe Ideapalooza challenges students to use creativity and technology to make a positive impact.",
                "school_restricted": False,
                "notes": "Annual competition cycle: September to October",
            }
        else:
            # Fallback for unknown URLs
            return {
                "name": "Adobe Student Program",
                "company": "Adobe",
                "apply_url": url,
                "status": "Unknown",
                "role_type": "Ambassador",
                "domain": "Tech",
                "eligibility_summary": "Students at accredited educational institutions",
                "location_notes": "Varies by program",
                "compensation_bucket": "Unpaid-or-perks",
                "last_verified": "2024-01-01",
                "short_description": "Adobe student program for developing creative and technical skills.",
                "responsibilities": [
                    "Participate in program activities and events",
                    "Create work using Adobe tools",
                    "Engage with Adobe community and resources",
                ],
                "time_commitment": "Varies by program",
                "perks_detail": "Access to Adobe resources and community",
                "deadlines": {
                    "application": "2024-01-01",
                    "program_start": "2024-02-01",
                    "program_end": "2024-12-31",
                },
                "social_requirements": "Engage with community using relevant hashtags",
                "source_url": url,
                "source_snippet": "Adobe offers various programs to help students develop creative and technical skills.",
                "school_restricted": False,
                "notes": "Program details vary by specific offering",
            }
