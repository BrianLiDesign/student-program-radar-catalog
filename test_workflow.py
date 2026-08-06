import asyncio
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import aiohttp
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from advanced_validation import AdvancedDataValidator
from deduplicate_programs import are_programs_duplicate
from generate_dashboard import (
    format_status_indicator,
    generate_compact_stats,
    generate_program_tables,
    generate_readme,
    get_apply_markdown,
)
from program_ids import generate_program_id
from scraper_framework import EnhancedBaseScraper, EnhancedScraperRegistry
from scraper_framework_async import AsyncBaseScraper
from track_history import ProgramHistoryTracker
from validate_data import load_schema, validate_programs


class DummyScraper(EnhancedBaseScraper):
    def find_program_urls(self):
        return [f"{self.base_url}/program"]

    def parse_program_page(self, url):
        return {
            "name": "Example Program",
            "apply_url": url,
        }


class DummyAsyncScraper(AsyncBaseScraper):
    def find_program_urls(self):
        return [f"{self.base_url}/program"]

    def parse_program_page(self, url):
        return {"name": "Example Program", "apply_url": url}


class FakeAsyncResponse:
    def __init__(self, status, content=b"<html><h1>Program</h1></html>"):
        self.status = status
        self._content = content

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientResponseError(
                request_info=MagicMock(real_url="https://example.com/program"),
                history=(),
                status=self.status,
            )

    async def read(self):
        return self._content


class FakeAsyncSession:
    def __init__(self, statuses):
        self.statuses = iter(statuses)
        self.calls = 0

    def get(self, url, timeout):
        self.calls += 1
        return FakeAsyncResponse(next(self.statuses))


class ProgramIdTests(unittest.TestCase):
    def test_generate_program_id_is_deterministic_uuid_v5(self):
        first = generate_program_id("Adobe", "Student Ambassador")
        second = generate_program_id("Adobe", "Student Ambassador")
        self.assertEqual(first, second)
        self.assertRegex(
            first,
            r"^[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        )

    def test_different_programs_get_different_ids(self):
        a = generate_program_id("Adobe", "Student Ambassador")
        b = generate_program_id("Microsoft", "Student Ambassador")
        self.assertNotEqual(a, b)


class ScraperFrameworkTests(unittest.TestCase):
    def setUp(self):
        self.scraper = DummyScraper(
            "Example", "https://example.com", enable_cache=False, rate_limit_delay=0
        )

    def tearDown(self):
        self.scraper.session.close()

    def test_initialization_sets_session_headers(self):
        self.assertEqual(self.scraper.company_name, "Example")
        self.assertEqual(self.scraper.base_url, "https://example.com")
        self.assertIn("Mozilla/5.0", self.scraper.session.headers["User-Agent"])

    def test_extract_helpers(self):
        soup = BeautifulSoup('<a href="https://example.com">Hello <b>World</b></a>', "html.parser")
        link = soup.find("a")
        self.assertEqual(self.scraper._extract_text(link), "HelloWorld")
        self.assertEqual(self.scraper._extract_attribute(link, "href"), "https://example.com")
        self.assertEqual(self.scraper._extract_text(None), "")

    def test_fetch_page_success(self):
        response = MagicMock()
        response.content = b"<html><h1>Program</h1></html>"
        response.raise_for_status.return_value = None
        self.scraper.session.get = MagicMock(return_value=response)

        page = self.scraper._fetch_page("https://example.com/program")

        self.assertEqual(page.h1.get_text(), "Program")
        self.scraper.session.get.assert_called_once_with("https://example.com/program", timeout=15)

    def test_fetch_page_failure_is_counted(self):
        self.scraper.session.get = MagicMock(side_effect=RequestException("offline"))

        self.assertIsNone(self.scraper._fetch_page("https://example.com/program"))
        self.assertEqual(self.scraper.stats["errors"], 1)

    @patch("scraper_framework.time.sleep", return_value=None)
    def test_scrape_programs_adds_metadata_and_id(self, _sleep):
        programs = self.scraper.scrape_programs()

        self.assertEqual(len(programs), 1)
        self.assertEqual(programs[0]["company"], "Example")
        self.assertEqual(programs[0]["source_url"], "https://example.com/program")
        self.assertEqual(programs[0]["id"], generate_program_id("Example", "Example Program"))


class AsyncScraperFrameworkTests(unittest.TestCase):
    @staticmethod
    def _make_scraper():
        return DummyAsyncScraper(
            "Example",
            "https://example.com",
            enable_cache=False,
            rate_limit_delay=0,
            max_concurrent_requests=1,
            retry_base_delay=0,
        )

    def test_non_retryable_404_is_not_retried(self):
        async def scenario():
            scraper = self._make_scraper()
            scraper.session = FakeAsyncSession([404])
            page = await scraper._fetch_page("https://example.com/program")
            return scraper, page

        scraper, page = asyncio.run(scenario())

        self.assertIsNone(page)
        self.assertEqual(scraper.session.calls, 1)
        self.assertEqual(scraper.stats["errors"], 1)

    def test_retry_sleep_releases_concurrency_slot(self):
        semaphore_states = []

        async def scenario():
            scraper = self._make_scraper()
            scraper.session = FakeAsyncSession([500, 200])

            async def record_sleep(_delay):
                semaphore_states.append(not scraper._semaphore.locked())

            with patch("scraper_framework_async.asyncio.sleep", side_effect=record_sleep):
                page = await scraper._fetch_page("https://example.com/program")
            return scraper, page

        scraper, page = asyncio.run(scenario())
        self.assertEqual(page.h1.get_text(), "Program")
        self.assertEqual(scraper.session.calls, 2)
        self.assertEqual(semaphore_states, [True])


class ScraperRegistryTests(unittest.TestCase):
    def test_register_and_get_scraper(self):
        registry = EnhancedScraperRegistry()
        registry.register_scraper("Example", DummyScraper)

        scraper = registry.get_scraper(
            "Example", "https://example.com", enable_cache=False, rate_limit_delay=0
        )

        self.assertIsInstance(scraper, DummyScraper)
        scraper.session.close()

    def test_missing_scraper_raises_value_error(self):
        with self.assertRaises(ValueError):
            EnhancedScraperRegistry().get_scraper("Missing", "https://example.com")


class CatalogValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_schema()

    def test_checked_in_catalog_matches_schema_and_has_unique_ids(self):
        programs = json.loads(
            (PROJECT_ROOT / "data" / "active" / "programs.json").read_text(encoding="utf-8")
        )

        self.assertEqual(validate_programs(programs, self.schema), [])
        ids = [program["id"] for program in programs]
        self.assertEqual(len(ids), len(set(ids)))

    def test_invalid_role_type_is_rejected(self):
        program = json.loads(
            (PROJECT_ROOT / "data" / "active" / "programs.json").read_text(encoding="utf-8")
        )[0]
        program["role_type"] = "Unsupported"

        self.assertTrue(validate_programs([program], self.schema))


class DashboardTests(unittest.TestCase):
    def test_discover_first_readme_includes_apply_column(self):
        programs = json.loads(
            (PROJECT_ROOT / "data" / "active" / "programs.json").read_text(encoding="utf-8")
        )
        non_closed = [p for p in programs if p.get("status") != "Closed"]

        tables = generate_program_tables(programs)
        stats = generate_compact_stats(programs)
        readme = generate_readme()

        self.assertIn("| Company | Program | Status | Comp | Location | Apply |", tables)
        self.assertNotIn(f"{format_status_indicator('Closed')} Closed", tables)
        self.assertIn(f"**Active Programs:** {len(non_closed)}", stats)
        self.assertIn("Automation Health", readme)
        self.assertIn(get_apply_markdown(non_closed[0]["apply_url"]), tables)
        self.assertEqual(format_status_indicator("Unknown"), "\u26aa")


class DataQualityToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.programs = json.loads(
            (PROJECT_ROOT / "data" / "active" / "programs.json").read_text(encoding="utf-8")
        )

    def test_advanced_validator_runs_for_checked_in_catalog(self):
        result = AdvancedDataValidator().validate_program_batch(self.programs)

        self.assertEqual(result["total_programs"], len(self.programs))
        self.assertGreaterEqual(result["overall_score"], 0)

    def test_duplicate_detector_returns_boolean(self):
        is_duplicate, score, _reason = are_programs_duplicate(
            self.programs[0], dict(self.programs[0])
        )

        self.assertTrue(is_duplicate)
        self.assertGreaterEqual(score, 0.8)

    def test_history_snapshot_records_its_filename(self):
        with tempfile.TemporaryDirectory() as history_dir:
            tracker = ProgramHistoryTracker(history_dir)
            metadata = tracker.record_snapshot(self.programs[:1], source="test")
            snapshot = json.loads(Path(metadata["snapshot_path"]).read_text(encoding="utf-8"))

            self.assertEqual(
                snapshot["metadata"]["snapshot_file"],
                Path(metadata["snapshot_path"]).name,
            )


if __name__ == "__main__":
    unittest.main()
