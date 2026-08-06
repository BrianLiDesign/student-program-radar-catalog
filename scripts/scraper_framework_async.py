#!/usr/bin/env python3
"""
Async-enhanced scraper framework for Student Program Radar Catalog
Provides asynchronous processing capabilities for large-scale data operations
"""

import asyncio
import hashlib
import logging
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import aiofiles
import aiohttp
from bs4 import BeautifulSoup

# Configure logging with rotation
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
log_dir = os.path.normpath(log_dir)
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'scraper_async.log')

# Configure rotating file handler to prevent huge log files
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# File handler with rotation (10 MB per file, keep 5 backups)
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
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
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cache')
CACHE_ENABLED = True
CACHE_EXPIRY_HOURS = 4  # Cache expires after 4 hours

class AsyncCacheManager:
    """Manages caching of web requests to improve performance and reduce load on target sites (async version)"""

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

    async def get(self, url: str) -> Optional[bytes]:
        """Retrieve cached content for URL if it exists and is not expired"""
        if not CACHE_ENABLED:
            return None

        key = self._get_cache_key(url)
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        # Check if cache is expired
        if time.time() - cache_path.stat().st_mtime > self.expiry_seconds:
            try:
                await asyncio.to_thread(cache_path.unlink)  # Delete expired cache
            except FileNotFoundError:
                pass  # Already deleted
            return None

        try:
            async with aiofiles.open(cache_path, 'rb') as f:
                return await f.read()
        except Exception as e:
            logger.warning(f"Error reading cache for {url}: {e}")
            return None

    async def set(self, url: str, content: bytes):
        """Store content in cache for URL"""
        if not CACHE_ENABLED:
            return

        key = self._get_cache_key(url)
        cache_path = self._get_cache_path(key)

        try:
            async with aiofiles.open(cache_path, 'wb') as f:
                await f.write(content)
        except Exception as e:
            logger.warning(f"Error writing cache for {url}: {e}")


class AsyncRateLimiter:
    """Implements rate limiting to be respectful to target websites (async version)"""

    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        self.domain_last_access = {}  # Track last access per domain
        self._lock = asyncio.Lock()

    async def wait_if_needed(self, url: str):
        """Wait if necessary to respect rate limits"""
        async with self._lock:
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


class AsyncBaseScraper(ABC):
    """Async base class for company-specific scrapers with caching and rate limiting"""

    def __init__(self, company_name: str, base_url: str,
                 enable_cache: bool = True,
                 rate_limit_delay: float = 1.0,
                 max_concurrent_requests: int = 5):
        self.company_name = company_name
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        # Set a realistic user agent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.logger = logging.getLogger(f"{__name__}.{company_name}")

        # Initialize performance enhancements
        self.cache_manager = AsyncCacheManager() if enable_cache else None
        self.rate_limiter = AsyncRateLimiter(min_delay=rate_limit_delay)
        self.max_concurrent_requests = max_concurrent_requests
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)

        # Statistics
        self.stats = {
            'requests_made': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0
        }

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    @abstractmethod
    def find_program_urls(self) -> List[str]:
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

    async def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page with caching and rate limiting (async version)
        """
        # Check cache first
        if self.cache_manager:
            cached_content = await self.cache_manager.get(url)
            if cached_content:
                self.stats['cache_hits'] += 1
                try:
                    return BeautifulSoup(cached_content, 'html.parser')
                except Exception as e:
                    self.logger.warning(f"Error parsing cached content for {url}: {e}")
                    # Fall through to fetch fresh content

        self.stats['cache_misses'] += 1

        # Apply rate limiting
        await self.rate_limiter.wait_if_needed(url)

        # Use semaphore to limit concurrent requests
        async with self._semaphore:
            try:
                self.logger.info(f"Fetching {url}")
                timeout = aiohttp.ClientTimeout(total=15)
                async with self.session.get(url, timeout=timeout) as response:
                    response.raise_for_status()
                    content = await response.read()

                    # Cache the content
                    if self.cache_manager:
                        await self.cache_manager.set(url, content)

                    self.stats['requests_made'] += 1
                    return BeautifulSoup(content, 'html.parser')

            except aiohttp.ClientError as e:
                self.logger.error(f"Failed to fetch {url}: {str(e)}")
                self.stats['errors'] += 1
                return None
            except Exception as e:
                self.logger.error(f"Unexpected error fetching {url}: {str(e)}")
                self.stats['errors'] += 1
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

    async def scrape_programs_async(self) -> List[dict]:
        """
        Async main scraping method that finds and parses all programs for this company
        Returns list of program dictionaries
        """
        self.logger.info(f"Starting async scrape for {self.company_name}")
        start_time = time.time()

        programs = []
        program_urls = self.find_program_urls()

        self.logger.info(f"Found {len(program_urls)} potential program URLs for {self.company_name}")

        # Process URLs concurrently with limited concurrency
        tasks = [self._process_program_url(url, i) for i, url in enumerate(program_urls)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            url = program_urls[i]
            if isinstance(result, Exception):
                self.logger.error(f"Error processing {url}: {str(result)}")
                self.stats['errors'] += 1
            elif result is not None:
                programs.append(result)
                self.logger.info(f"Successfully parsed program: {result.get('name', 'Unknown')}")
            else:
                self.logger.warning(f"No valid program data found at {url}")

        end_time = time.time()
        duration = end_time - start_time

        self.logger.info(f"Completed async scrape for {self.company_name} in {duration:.2f} seconds")
        self.logger.info(f"Stats: {self.stats}")

        return programs

    async def _process_program_url(self, url: str, index: int) -> Optional[dict]:
        """Process a single program URL"""
        try:
            self.logger.debug(f"Processing URL {index+1}: {url}")
            program_data = await self._parse_program_page_async(url)

            if program_data:
                # Add metadata
                program_data['company'] = self.company_name
                program_data['source_url'] = url

                # Generate consistent ID if not present
                if 'id' not in program_data or not program_data['id']:
                    program_data['id'] = self._generate_program_id(program_data)

                return program_data
            else:
                self.logger.warning(f"No valid program data found at {url}")
                return None

        except Exception as e:
            self.logger.error(f"Error processing {url}: {str(e)}")
            self.stats['errors'] += 1
            return None

    async def _parse_program_page_async(self, url: str) -> Optional[dict]:
        """
        Parse a program page asynchronously (wrapper for the synchronous parse method)
        Since parsing is CPU-bound rather than I/O-bound, we run it in a thread pool
        """
        # Fetch the page (this is the I/O bound part that benefits from async)
        soup = await self._fetch_page(url)
        if not soup:
            return None

        # Run the parsing in a thread pool since it's CPU-intensive
        loop = asyncio.get_event_loop()
        try:
            # Parse the page (this is the CPU-bound work that doesn't benefit much from async but we don't want to block)
            result = await loop.run_in_executor(
                None,
                self.parse_program_page,
                url
            )
            return result
        except Exception as e:
            self.logger.error(f"Error parsing {url}: {str(e)}")
            return None

    def _generate_program_id(self, program_data: dict) -> str:
        """
        Generate a consistent ID for a program based on its attributes
        Uses company name and program name for consistency
        """
        company = program_data.get('company', self.company_name)
        name = program_data.get('name', 'unknown')

        # Create a deterministic ID
        id_string = f"{company}_{name}".lower()
        # Replace spaces and special characters
        import re
        id_string = re.sub(r'[^a-z0-9]+', '_', id_string)
        # Remove leading/trailing underscores
        id_string = id_string.strip('_')
        # Limit length
        if len(id_string) > 50:
            id_string = id_string[:50]

        return id_string

    def get_stats(self) -> dict:
        """Get scraping statistics"""
        return self.stats.copy()


class AsyncScraperRegistry:
    """Async registry to manage all company scrapers with statistics"""

    def __init__(self):
        self.scrapers = {}
        self.global_stats = {
            'total_scrapers': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'total_programs_found': 0
        }

    def register_scraper(self, company_name: str, scraper_class):
        """Register a scraper class for a company"""
        self.scrapers[company_name] = scraper_class
        self.global_stats['total_scrapers'] += 1

    def get_scraper(self, company_name: str, base_url: str, **kwargs):
        """Get an instance of a scraper for a company"""
        if company_name not in self.scrapers:
            raise ValueError(f"No scraper registered for company: {company_name}")
        return self.scrapers[company_name](company_name, base_url, **kwargs)

    async def scrape_all_companies_async(self, company_configs: List[dict]) -> List[dict]:
        """
        Async scrapes all configured companies
        company_configs: list of dicts with 'name' and 'base_url' keys
        """
        all_programs = []

        # Create tasks for each company
        tasks = []
        for config in company_configs:
            company_name = config['name']
            base_url = config['base_url']

            task = self._scrape_single_company(company_name, base_url)
            tasks.append(task)

        # Wait for all companies to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            config = company_configs[i]
            company_name = config['name']

            if isinstance(result, Exception):
                self.logger.error(f"Failed to scrape {company_name}: {str(result)}")
                self.global_stats['failed_scrapes'] += 1
            elif isinstance(result, list):
                all_programs.extend(result)
                self.global_stats['successful_scrapes'] += 1
                self.global_stats['total_programs_found'] += len(result)
                print(f"Scraped {len(result)} programs from {company_name}")

        return all_programs

    async def _scrape_single_company(self, company_name: str, base_url: str) -> List[dict]:
        """Scrape a single company"""
        try:
            scraper_class = self.scrapers[company_name]
            # For async scrapers, we need to use the async context manager
            if hasattr(scraper_class, '__aenter__'):
                async with scraper_class(company_name, base_url) as scraper:
                    return await scraper.scrape_programs_async()
            else:
                # Fallback to regular scraper if not async-capable
                scraper = scraper_class(company_name, base_url)
                return scraper.scrape_programs()  # This is sync, but we're already in async context
        except Exception as e:
            self.logger.error(f"Error in _scrape_single_company for {company_name}: {str(e)}")
            raise

    def get_global_stats(self) -> dict:
        """Get global scraping statistics"""
        return self.global_stats.copy()


# Global registry instance
async_scraper_registry = AsyncScraperRegistry()

# Helper function to run async scrapers from sync contexts
def run_async_scrape_companies(company_configs: List[dict]) -> List[dict]:
    """
    Helper function to run the async scraping from a synchronous context
    """
    return asyncio.run(async_scraper_registry.scrape_all_companies_async(company_configs))


if __name__ == "__main__":
    # This is just for testing the framework
    print("Async scraper framework loaded successfully")
    print("To use: inherit from AsyncBaseScraper and implement the abstract methods")