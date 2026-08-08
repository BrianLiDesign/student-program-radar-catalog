#!/usr/bin/env python3
"""
Enhanced scraper framework for Student Program Radar Catalog
With caching, rate limiting, and performance optimizations
"""

import asyncio
import hashlib
import logging
import os
import random
import time
from abc import ABC, abstractmethod
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import aiohttp
import requests
from bs4 import BeautifulSoup

from program_ids import generate_program_id

# Configure logging with rotation
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
log_dir = os.path.normpath(log_dir)
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "scraper.log")

# Configure rotating file handler to prevent huge log files

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# File handler with rotation (10 MB per file, keep 5 backups)
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
)
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.handlers = []  # Clear any existing handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Cache configuration
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache")
CACHE_ENABLED = True
CACHE_EXPIRY_HOURS = 4  # Cache expires after 4 hours


class CacheManager:
    """Manages caching of web requests to improve performance and reduce load on target sites.

    Note: The async methods (async_get, async_set) currently delegate to the synchronous
    versions since file I/O is typically fast enough for caching purposes. For very high-scale
    applications, these could be enhanced to use aiofiles for true async file operations.
    """

    def __init__(self, cache_dir: str = CACHE_DIR, expiry_hours: int = CACHE_EXPIRY_HOURS):
        self.cache_dir = Path(cache_dir)
        self.expiry_seconds = expiry_hours * 3600
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, url: str) -> str:
        """Generate a cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key"""
        return self.cache_dir / f"{key}.cache"

    def get(self, url: str) -> Optional[bytes]:
        """Retrieve cached content for URL if it exists and is not expired"""
        if not CACHE_ENABLED:
            return None

        key = self._get_cache_key(url)
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        # Check if cache is expired
        if time.time() - cache_path.stat().st_mtime > self.expiry_seconds:
            cache_path.unlink()  # Delete expired cache
            return None

        try:
            with open(cache_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Error reading cache for {url}: {e}")
            return None

    def set(self, url: str, content: bytes):
        """Store content in cache for URL"""
        if not CACHE_ENABLED:
            return

        key = self._get_cache_key(url)
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, "wb") as f:
                f.write(content)
        except Exception as e:
            logger.warning(f"Error writing cache for {url}: {e}")

    async def async_get(self, url: str) -> Optional[bytes]:
        """Async version of get"""
        # For file I/O, we can use the synchronous version as it's fast
        # In a high-scale applications, we might use aiofiles, but for cache it's usually fine
        return self.get(url)

    async def async_set(self, url: str, content: bytes):
        """Async version of set"""
        # For file I/O, we can use the synchronous version as it's fast
        return self.set(url, content)


class RateLimiter:
    """Implements rate limiting to be respectful to target websites"""

    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        self.domain_last_access = {}  # Track last access per domain

    def wait_if_needed(self, url: str):
        """Wait if necessary to respect rate limits"""
        parsed = urlparse(url)
        domain = parsed.netloc

        # Global rate limit
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)

        # Domain-specific rate limit (be even more gentle with same domain)
        if domain in self.domain_last_access:
            domain_elapsed = time.time() - self.domain_last_access[domain]
            if domain_elapsed < self.min_delay * 2:  # Wait longer between requests to same domain
                time.sleep((self.min_delay * 2) - domain_elapsed)

        # Update timestamps
        self.last_request_time = time.time()
        self.domain_last_access[domain] = self.last_request_time

    async def async_wait_if_needed(self, url: str):
        """Async version of wait_if_needed"""
        parsed = urlparse(url)
        domain = parsed.netloc

        # Global rate limit
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            await asyncio.sleep(self.min_delay - elapsed)

        # Domain-specific rate limit (be even more gentle with same domain)
        if domain in self.domain_last_access:
            domain_elapsed = time.time() - self.domain_last_access[domain]
            if domain_elapsed < self.min_delay * 2:  # Wait longer between requests to same domain
                await asyncio.sleep((self.min_delay * 2) - domain_elapsed)

        # Update timestamps
        self.last_request_time = time.time()
        self.domain_last_access[domain] = self.last_request_time


class EnhancedBaseScraper(ABC):
    """Enhanced base class for company-specific scrapers with caching and rate limiting"""

    def __init__(
        self,
        company_name: str,
        base_url: str,
        enable_cache: bool = True,
        rate_limit_delay: float = 1.0,
        max_concurrent_requests: int = 5,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
        retry_max_delay: float = 30.0,
    ):
        self.company_name = company_name
        self.base_url = base_url
        self.enable_cache = enable_cache
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.retry_max_delay = retry_max_delay

        # Set a realistic user agent
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        self.logger = logging.getLogger(f"{__name__}.{company_name}")

        # Initialize performance enhancements
        self.cache_manager = CacheManager() if enable_cache else None
        self.rate_limiter = RateLimiter(min_delay=rate_limit_delay)
        self.max_concurrent_requests = max_concurrent_requests

        # Statistics
        self.stats = {"requests_made": 0, "cache_hits": 0, "cache_misses": 0, "errors": 0}

        # Initialize session for sync requests
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def __del__(self):
        """Cleanup session"""
        if hasattr(self, "session") and self.session:
            self.session.close()

    @abstractmethod
    def find_program_urls(self) -> list[str]:
        """
        Find URLs for student programs on the company's site
        Should return a list of URLs to scrape
        """
        pass

    @abstractmethod
    def parse_program_page(self, url: str) -> Optional[dict]:
        """
        Parse a single program page and return program data as dict
        Returns None if no valid program found at the URL
        """
        pass

    def _is_retryable_error(self, error: Exception, status_code: Optional[int] = None) -> bool:
        """Return True for transient network or server errors."""
        if status_code is not None:
            if status_code == 429 or 500 <= status_code < 600:
                return True
            if 400 <= status_code < 500:
                return False
        if isinstance(error, (requests.Timeout, requests.ConnectionError)):
            return True
        if isinstance(error, requests.HTTPError) and error.response is not None:
            code = error.response.status_code
            return code == 429 or 500 <= code < 600
        return False

    def _fetch_page(self, url: str, timeout: int = 15) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page with caching, rate limiting, and retries.
        """
        # Check cache first
        if self.cache_manager:
            cached_content = self.cache_manager.get(url)
            if cached_content:
                self.stats["cache_hits"] += 1
                try:
                    return BeautifulSoup(cached_content, "html.parser")
                except Exception as e:
                    self.logger.warning(f"Error parsing cached content for {url}: {e}")
                    # Fall through to fetch fresh content

        self.stats["cache_misses"] += 1

        for attempt in range(self.max_retries + 1):
            self.rate_limiter.wait_if_needed(url)

            try:
                self.logger.info(
                    f"Fetching {url}" + (f" (attempt {attempt + 1})" if attempt else "")
                )
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()

                if self.cache_manager:
                    self.cache_manager.set(url, response.content)

                self.stats["requests_made"] += 1
                return BeautifulSoup(response.content, "html.parser")

            except requests.HTTPError as e:
                status_code = e.response.status_code if e.response is not None else None
                if attempt < self.max_retries and self._is_retryable_error(e, status_code):
                    delay = min(
                        self.retry_base_delay * (2**attempt) + random.uniform(0, 0.5),
                        self.retry_max_delay,
                    )
                    self.logger.warning(
                        f"HTTP {status_code} for {url}, retrying in {delay:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(delay)
                    continue
                self.logger.error(f"Failed to fetch {url}: {str(e)}")
                self.stats["errors"] += 1
                return None
            except requests.RequestException as e:
                if attempt < self.max_retries and self._is_retryable_error(e):
                    delay = min(
                        self.retry_base_delay * (2**attempt) + random.uniform(0, 0.5),
                        self.retry_max_delay,
                    )
                    self.logger.warning(
                        f"Request error for {url}, retrying in {delay:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(delay)
                    continue
                self.logger.error(f"Failed to fetch {url}: {str(e)}")
                self.stats["errors"] += 1
                return None
            except Exception as e:
                self.logger.error(f"Unexpected error fetching {url}: {str(e)}")
                self.stats["errors"] += 1
                return None

        return None

    def _extract_text(self, element) -> str:
        """Safely extract text from a BeautifulSoup element"""
        if element:
            return element.get_text(strip=True)
        return ""

    def _extract_attribute(self, element, attr: str) -> str:
        """Safely extract attribute from a BeautifulSoup element"""
        if element and element.has_attr(attr):
            return element[attr]
        return ""

    def scrape_programs(self) -> list[dict]:
        """
        Enhanced main scraping method that finds and parses all programs for this company
        Returns list of program dictionaries
        """
        self.logger.info(f"Starting scrape for {self.company_name}")
        start_time = time.time()

        programs = []
        program_urls = self.find_program_urls()

        self.logger.info(
            f"Found {len(program_urls)} potential program URLs for {self.company_name}"
        )

        # Process URLs with progress tracking
        for i, url in enumerate(program_urls, 1):
            try:
                self.logger.debug(f"Processing URL {i}/{len(program_urls)}: {url}")
                program_data = self.parse_program_page(url)

                if program_data:
                    # Add metadata
                    program_data["company"] = self.company_name
                    program_data["source_url"] = url

                    # Generate consistent ID if not present
                    if "id" not in program_data or not program_data["id"]:
                        program_data["id"] = self._generate_program_id(program_data)

                    programs.append(program_data)
                    self.logger.info(
                        f"Successfully parsed program: {program_data.get('name', 'Unknown')}"
                    )
                else:
                    self.logger.warning(f"No valid program data found at {url}")

                # Add a small delay between processing to be extra gentle
                if i < len(program_urls):  # Don't sleep after the last item
                    time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Error processing {url}: {str(e)}")
                self.stats["errors"] += 1
                continue

        end_time = time.time()
        duration = end_time - start_time

        self.logger.info(f"Completed scrape for {self.company_name} in {duration:.2f} seconds")
        self.logger.info(f"Stats: {self.stats}")

        return programs

    def _generate_program_id(self, program_data: dict) -> str:
        """Generate a deterministic UUID v5 for a program."""
        company = program_data.get("company", self.company_name)
        name = program_data.get("name", "unknown")
        return generate_program_id(company, name)

    def get_stats(self) -> dict:
        """Get scraping statistics"""
        return self.stats.copy()

    # Async methods for high-concurrency scraping
    async def _fetch_page_async(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page with caching and rate limiting (async version)
        """
        # Check cache first
        if self.cache_manager:
            cached_content = await self.cache_manager.async_get(url)
            if cached_content:
                self.stats["cache_hits"] += 1
                try:
                    return BeautifulSoup(cached_content, "html.parser")
                except Exception as e:
                    self.logger.warning(f"Error parsing cached content for {url}: {e}")
                    # Fall through to fetch fresh content

        self.stats["cache_misses"] += 1

        # Apply rate limiting
        await self.rate_limiter.async_wait_if_needed(url)

        # Create a new session for this request
        # Note: For improved efficiency in high-scale applications, consider reusing
        # a single ClientSession instance rather than creating one per request.
        timeout = aiohttp.ClientTimeout(total=15)
        try:
            async with aiohttp.ClientSession() as session:
                session.headers.update(self.headers)
                self.logger.info(f"Fetching {url}")
                async with session.get(url, timeout=timeout) as response:
                    response.raise_for_status()
                    content = await response.read()

                    # Cache the content
                    if self.cache_manager:
                        await self.cache_manager.async_set(url, content)

                    self.stats["requests_made"] += 1
                    return BeautifulSoup(content, "html.parser")

        except aiohttp.ClientError as e:
            self.logger.error(f"Failed to fetch {url}: {str(e)}")
            self.stats["errors"] += 1
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {url}: {str(e)}")
            self.stats["errors"] += 1
            return None

    async def _parse_program_page_async(self, url: str) -> Optional[dict]:
        """
        Parse a program page asynchronously (wrapper for the synchronous parse method)
        Since parsing is CPU-bound rather than I/O-bound, we run it in a thread pool
        """
        # Fetch the page (this is the I/O bound part that benefits from async)
        soup = await self._fetch_page_async(url)
        if not soup:
            return None

        # Run the parsing in a thread pool since it's CPU-intensive
        loop = asyncio.get_event_loop()
        try:
            # Parse the page (this is the CPU-bound part)
            program_data = await loop.run_in_executor(None, self.parse_program_page, url)
            return program_data
        except Exception as e:
            self.logger.error(f"Error parsing {url}: {str(e)}")
            self.stats["errors"] += 1
            return None

    async def scrape_programs_async(self) -> list[dict]:
        """
        Async main scraping method that finds and parses all programs for this company
        Returns list of program dictionaries
        """
        self.logger.info(f"Starting async scrape for {self.company_name}")
        start_time = time.time()

        programs = []
        program_urls = self.find_program_urls()

        self.logger.info(
            f"Found {len(program_urls)} potential program URLs for {self.company_name}"
        )

        # Process URLs concurrently with limited concurrency
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)

        async def process_url_with_semaphore(url: str, index: int) -> Optional[dict]:
            async with semaphore:
                try:
                    self.logger.debug(f"Processing URL {index + 1}: {url}")
                    program_data = await self._parse_program_page_async(url)

                    if program_data:
                        # Add metadata
                        program_data["company"] = self.company_name
                        program_data["source_url"] = url

                        # Generate consistent ID if not present
                        if "id" not in program_data or not program_data["id"]:
                            program_data["id"] = self._generate_program_id(program_data)

                        return program_data
                    else:
                        self.logger.warning(f"No valid program data found at {url}")
                        return None

                except Exception as e:
                    self.logger.error(f"Error processing {url}: {str(e)}")
                    self.stats["errors"] += 1
                    return None

        # Create tasks for all URLs
        tasks = [process_url_with_semaphore(url, i) for i, url in enumerate(program_urls)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            url = program_urls[i]
            if isinstance(result, Exception):
                self.logger.error(f"Error processing {url}: {str(result)}")
                self.stats["errors"] += 1
            elif result is not None:
                programs.append(result)
                self.logger.info(f"Successfully parsed program: {result.get('name', 'Unknown')}")
            else:
                self.logger.warning(f"No valid program data found at {url}")

        end_time = time.time()
        duration = end_time - start_time

        self.logger.info(
            f"Completed async scrape for {self.company_name} in {duration:.2f} seconds"
        )
        self.logger.info(f"Stats: {self.stats}")

        return programs


class EnhancedScraperRegistry:
    """Enhanced registry to manage all company scrapers with statistics"""

    def __init__(self):
        self.scrapers = {}
        self.logger = logging.getLogger(f"{__name__}.registry")
        self.global_stats = {
            "total_scrapers": 0,
            "successful_scrapes": 0,
            "failed_scrapes": 0,
            "total_programs_found": 0,
        }

    def register_scraper(self, company_name: str, scraper_class):
        """Register a scraper class for a company"""
        self.scrapers[company_name] = scraper_class
        self.global_stats["total_scrapers"] += 1

    def get_scraper(self, company_name: str, base_url: str, **kwargs):
        """Get an instance of a scraper for a company"""
        if company_name not in self.scrapers:
            raise ValueError(f"No scraper registered for company: {company_name}")
        return self.scrapers[company_name](company_name, base_url, **kwargs)

    def scrape_all_companies(self, company_configs: list[dict]) -> list[dict]:
        """
        Scrape all configured companies
        company_configs: list of dicts with 'name' and 'base_url' keys
        """
        all_programs = []

        for config in company_configs:
            company_name = config["name"]
            base_url = config.get("base_url", "")

            # If no base_url is provided, try to construct a reasonable one
            if not base_url:
                # Try to guess the website URL based on company name
                # This is a simplified approach - in reality, we might want to store URLs in the allowlist
                guessed_url = f"https://www.{company_name.lower().replace(' ', '')}.com"
                base_url = guessed_url
                logger.warning(
                    f"No base_url provided for {company_name}, using guessed URL: {base_url}"
                )

            try:
                scraper = self.get_scraper(company_name, base_url)
                # Use the async version for better performance - but we need to run it in a sync context
                # For now, we'll stick with the sync version to maintain compatibility with existing code
                programs = scraper.scrape_programs()
                all_programs.extend(programs)
                self.global_stats["successful_scrapes"] += 1
                self.global_stats["total_programs_found"] += len(programs)
                print(f"Scraped {len(programs)} programs from {company_name}")
            except Exception as e:
                self.logger.error(f"Failed to scrape {company_name}: {str(e)}")
                self.global_stats["failed_scrapes"] += 1
                continue

        return all_programs

    def get_global_stats(self) -> dict:
        """Get global scraping statistics"""
        return self.global_stats.copy()


# Global registry instance
scraper_registry = EnhancedScraperRegistry()


def register_scrapers():
    """Import and register all scrapers from the config/scrapers directory"""
    import os
    import sys

    # Add config/scrapers to the path
    scrapers_dir = os.path.join(os.path.dirname(__file__), "..", "config", "scrapers")
    scrapers_dir = os.path.normpath(scrapers_dir)

    if os.path.exists(scrapers_dir):
        if scrapers_dir not in sys.path:
            sys.path.append(scrapers_dir)

    # Import each scraper file and register its scraper classes
    for filename in os.listdir(scrapers_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # Remove .py extension
            try:
                module = __import__(module_name)
                # Look for classes in the module that inherit from EnhancedBaseScraper
                for item_name in dir(module):
                    item = getattr(module, item_name)
                    if (
                        isinstance(item, type)
                        and issubclass(item, EnhancedBaseScraper)
                        and item != EnhancedBaseScraper
                    ):
                        # Extract company name from the class name or use a default
                        # For example, GitHubScraper -> github
                        company_name = item_name.replace("Scraper", "")
                        # Handle special cases like GitHubScraper -> GitHub
                        if company_name == "GitHub":
                            pass  # Keep as is
                        # Register the scraper
                        scraper_registry.register_scraper(company_name, item)
                        logger.info(f"Registered scraper: {company_name} -> {item_name}")
            except Exception as e:
                logger.error(f"Failed to load scraper {module_name}: {e}")


# Register scrapers when module is imported
register_scrapers()

if __name__ == "__main__":
    # This is just for testing the framework
    print("Enhanced scraper framework loaded successfully")
    print(f"Registered scrapers: {list(scraper_registry.scrapers.keys())}")
