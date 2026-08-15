#!/usr/bin/env python3
"""Mocked HTTP tests for batch 2026-08-08 company expansion scrapers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "config" / "scrapers"))

from amd_scraper import UNIVERSITY_PROGRAM_URL, AMDScraper
from arm_scraper import EDUCATION_URL as ARM_EDUCATION_URL
from arm_scraper import ArmScraper
from canva_scraper import EDUCATION_URL as CANVA_EDUCATION_URL
from canva_scraper import CanvaScraper
from coursera_scraper import CAMPUS_URL, CourseraScraper
from databricks_scraper import TRAINING_HOME_URL, DatabricksScraper
from elastic_scraper import TRAINING_URL as ELASTIC_TRAINING_URL
from elastic_scraper import ElasticScraper
from figma_scraper import HIGHER_ED_URL, FigmaScraper
from google_scraper import COMMUNITY_URL, GoogleScraper
from ibm_scraper import UNIVERSITY_STUDENTS_URL, IBMScraper
from jetbrains_scraper import ACADEMY_URL, JetBrainsScraper
from mongodb_scraper import STUDENTS_URL, MongoDBScraper
from notion_scraper import EDUCATION_HELP_URL, NotionScraper
from nvidia_scraper import TRAINING_URL as NVIDIA_TRAINING_URL
from nvidia_scraper import NVIDIAScraper
from salesforce_scraper import STUDENT_PROGRAM_URL, SalesforceScraper
from unity_scraper import EDUCATION_URL as UNITY_EDUCATION_URL
from unity_scraper import UnityScraper

from program_ids import generate_program_id

GOOGLE_HTML = """
<html><body>
<h2>Lead a GDG</h2>
<p>Google Developer Groups on Campus help students lead local developer communities.</p>
<a href="https://app.advocu.com/gdg/join">Lead a GDG on Campus</a>
</body></html>
"""

IBM_HTML = """
<html><body>
<h1>IBM SkillsBuild for University Students</h1>
<p>Sign up now and get a head start on life after graduation with free AI training.</p>
<a href="https://skillsbuild.org/sign-up">Sign up</a>
</body></html>
"""

MONGODB_HTML = """
<html><body>
<h1>MongoDB for Students</h1>
<p>Get MongoDB Atlas credits and certifications through the MongoDB Student Pack.</p>
<p>Students can apply for benefits through the GitHub Student Developer Pack.</p>
</body></html>
"""

FIGMA_HTML = """
<html><body>
<h1>Students and faculty get Figma for free</h1>
<p>Learn valuable skills in design, UX, and prototyping with a free Education plan.</p>
<a href="https://www.figma.com/education/apply">Verify your student status</a>
</body></html>
"""

JETBRAINS_HTML = """
<html><body>
<h2>Jumpstart your career with essential developer skills</h2>
<p>JetBrains Academy helps students learn through hands-on projects and courses.</p>
<a href="https://www.jetbrains.com/academy/sign-up">Get started</a>
</body></html>
"""

CANVA_HTML = """
<html><body>
<h1>Canva for Education</h1>
<p>Bring creativity to your classroom with Canva for Education for students and teachers.</p>
<a href="https://www.canva.com/signup">Sign up</a>
</body></html>
"""

DATABRICKS_HTML = """
<html><body>
<h1>Databricks Academy</h1>
<p>Start learning data engineering and machine learning with free Databricks training.</p>
</body></html>
"""

NOTION_HTML = """
<html><body>
<h1>Notion for education</h1>
<p>Notion for Education helps students and teachers organize coursework and campus projects.</p>
<a href="https://www.notion.so/signup">Sign up</a>
</body></html>
"""

NVIDIA_HTML = """
<html><body>
<h1>NVIDIA Training</h1>
<p>Students can enroll in NVIDIA training courses on AI and accelerated computing.</p>
</body></html>
"""

SALESFORCE_HTML = """
<html><body>
<h1>Student Program</h1>
<p>The Salesforce Student Program helps students learn CRM skills on Trailhead.</p>
<p>Students can apply to join the program and start learning today.</p>
</body></html>
"""

AMD_HTML = """
<html><body>
<h1>AMD University Program</h1>
<p>Hub for educators, researchers and students to access AMD resources and programs.</p>
</body></html>
"""

ARM_HTML = """
<html><body>
<h1>Arm Education</h1>
<p>Arm Education helps students and educators learn embedded systems development.</p>
<a href="https://www.arm.com/learn">Start learning</a>
</body></html>
"""

COURSERA_HTML = """
<html><body>
<h1>Empower employability with online learning</h1>
<p>Coursera for Campus equips students with in-demand skills for job success.</p>
<a href="https://www.coursera.org/campus/contact">Contact us</a>
</body></html>
"""

ELASTIC_HTML = """
<html><body>
<h1>Elastic Training</h1>
<p>Build search, security, and observability skills with Elastic training courses.</p>
</body></html>
"""

UNITY_HTML = """
<html><body>
<h1>Prepare students to create the future with Unity Education</h1>
<p>Teach real-time 3D skills for careers in games, XR, and interactive media.</p>
<a href="https://unity.com/contact">Contact us</a>
</body></html>
"""


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


class ExpansionScraperTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)

    def test_google_scraper_parses_gdg_on_campus(self):
        scraper = GoogleScraper("Google", "https://developers.google.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(GOOGLE_HTML)):
            program = scraper.parse_program_page(COMMUNITY_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Google Developer Groups on Campus Lead")
        self.assertEqual(program["status"], "Accepting")

    def test_ibm_scraper_parses_university_students_page(self):
        scraper = IBMScraper("IBM", "https://skillsbuild.org")
        with patch.object(scraper, "_fetch_page", return_value=_soup(IBM_HTML)):
            program = scraper.parse_program_page(UNIVERSITY_STUDENTS_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertIn("SkillsBuild", program["name"])
        self.assertIn("skillsbuild.org", program["apply_url"])

    def test_mongodb_scraper_parses_students_page(self):
        scraper = MongoDBScraper("MongoDB", "https://www.mongodb.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(MONGODB_HTML)):
            program = scraper.parse_program_page(STUDENTS_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "MongoDB for Students")

    def test_figma_scraper_parses_higher_education_page(self):
        scraper = FigmaScraper("Figma", "https://www.figma.com/education")
        with patch.object(scraper, "_fetch_page", return_value=_soup(FIGMA_HTML)):
            program = scraper.parse_program_page(HIGHER_ED_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Figma for Education")
        self.assertIn("education/apply", program["apply_url"])

    def test_jetbrains_scraper_parses_academy_page(self):
        scraper = JetBrainsScraper("JetBrains", "https://www.jetbrains.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(JETBRAINS_HTML)):
            program = scraper.parse_program_page(ACADEMY_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "JetBrains Academy for Students")

    def test_expansion_program_ids_are_stable(self):
        scraper = IBMScraper("IBM", "https://skillsbuild.org")
        with patch.object(scraper, "_fetch_page", return_value=_soup(IBM_HTML)):
            program = scraper.parse_program_page(UNIVERSITY_STUDENTS_URL)

        assert program is not None
        expected = generate_program_id("IBM", "IBM SkillsBuild for University Students")
        self.assertEqual(generate_program_id(program["company"], program["name"]), expected)

    def test_canva_scraper_parses_education_page(self):
        scraper = CanvaScraper("Canva", "https://www.canva.com/education")
        with patch.object(scraper, "_fetch_page", return_value=_soup(CANVA_HTML)):
            program = scraper.parse_program_page(CANVA_EDUCATION_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Canva for Education")

    def test_databricks_scraper_parses_training_home(self):
        scraper = DatabricksScraper("Databricks", "https://www.databricks.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(DATABRICKS_HTML)):
            program = scraper.parse_program_page(TRAINING_HOME_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Databricks Academy")

    def test_notion_scraper_parses_education_help(self):
        scraper = NotionScraper("Notion", "https://www.notion.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(NOTION_HTML)):
            program = scraper.parse_program_page(EDUCATION_HELP_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Notion for Education")

    def test_nvidia_scraper_parses_training_page(self):
        scraper = NVIDIAScraper("NVIDIA", "https://www.nvidia.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(NVIDIA_HTML)):
            program = scraper.parse_program_page(NVIDIA_TRAINING_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "NVIDIA Training for Students")

    def test_salesforce_scraper_parses_student_program(self):
        scraper = SalesforceScraper("Salesforce", "https://trailhead.salesforce.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(SALESFORCE_HTML)):
            program = scraper.parse_program_page(STUDENT_PROGRAM_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Salesforce Student Program")

    def test_amd_scraper_parses_university_program(self):
        scraper = AMDScraper("AMD", "https://www.amd.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(AMD_HTML)):
            program = scraper.parse_program_page(UNIVERSITY_PROGRAM_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "AMD University Program")

    def test_arm_scraper_parses_education_page(self):
        scraper = ArmScraper("Arm", "https://www.arm.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(ARM_HTML)):
            program = scraper.parse_program_page(ARM_EDUCATION_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Arm Education")

    def test_coursera_scraper_parses_campus_page(self):
        scraper = CourseraScraper("Coursera", "https://www.coursera.org")
        with patch.object(scraper, "_fetch_page", return_value=_soup(COURSERA_HTML)):
            program = scraper.parse_program_page(CAMPUS_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Coursera for Campus")

    def test_elastic_scraper_parses_training_page(self):
        scraper = ElasticScraper("Elastic", "https://www.elastic.co")
        with patch.object(scraper, "_fetch_page", return_value=_soup(ELASTIC_HTML)):
            program = scraper.parse_program_page(ELASTIC_TRAINING_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Elastic Training")

    def test_unity_scraper_parses_education_page(self):
        scraper = UnityScraper("Unity", "https://unity.com")
        with patch.object(scraper, "_fetch_page", return_value=_soup(UNITY_HTML)):
            program = scraper.parse_program_page(UNITY_EDUCATION_URL)

        self.assertIsNotNone(program)
        assert program is not None
        self.assertEqual(program["name"], "Unity Education")


if __name__ == "__main__":
    unittest.main()
