#!/usr/bin/env python3
"""
Main scraping script for Student Program Radar Catalog
Loads company allowlist and runs scrapers for each company
"""

import json
import logging
import os
import sys

# Add the scripts directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))

from generate_dashboard import get_project_root
from scraper_framework import scraper_registry
from validate_data import load_schema, validate_programs

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(os.path.join(LOG_DIR, "scraper.log")), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def load_allowlist() -> list[dict]:
    """
    Load company allowlist from config file
    """
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "allowlist.json")
    config_path = os.path.normpath(config_path)

    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("companies", [])
    except Exception as e:
        logger.error(f"Failed to load allowlist: {e}")
        return []


def scrape_company_programs(company_config: dict) -> list[dict]:
    """
    Scrape programs for a single company
    """
    company_name = company_config["name"]
    base_url = company_config.get("base_url", "")

    # If no base_url is provided, try to construct a reasonable one
    if not base_url:
        # Try to guess the website URL based on company name
        # This is a simplified approach - in reality, we might want to store URLs in the allowlist
        guessed_url = f"https://www.{company_name.lower().replace(' ', '')}.com"
        base_url = guessed_url
        logger.warning(f"No base_url provided for {company_name}, using guessed URL: {base_url}")

    try:
        scraper = scraper_registry.get_scraper(company_name, base_url)
        programs = scraper.scrape_programs()
        logger.info(f"Scraped {len(programs)} programs from {company_name}")
        return programs
    except ValueError as e:
        # No scraper registered for this company
        logger.info(f"No scraper available for {company_name}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error scraping {company_name}: {e}")
        return []


def load_existing_programs(filepath: str) -> list[dict]:
    """
    Load existing programs from JSON file
    """
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading existing programs from {filepath}: {e}")
        return []


def save_programs(filepath: str, programs: list[dict]):
    """
    Save programs to JSON file
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(programs, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(programs)} programs to {filepath}")
    except Exception as e:
        logger.error(f"Error saving programs to {filepath}: {e}")


def merge_programs(existing: list[dict], new: list[dict]) -> list[dict]:
    """
    Merge new programs with existing ones, avoiding duplicates by ID
    """
    # Start with a de-duplicated copy of existing programs.
    merged = []
    id_to_index = {}
    for program in existing:
        prog_id = program.get("id")
        if prog_id and prog_id in id_to_index:
            merged[id_to_index[prog_id]] = program
        else:
            merged.append(program)
            if prog_id:
                id_to_index[prog_id] = len(merged) - 1

    # Add or update with new programs
    for new_prog in new:
        prog_id = new_prog.get("id")
        if prog_id:
            if prog_id in id_to_index:
                # Update existing program
                idx = id_to_index[prog_id]
                merged[idx] = new_prog
                logger.info(f"Updated existing program: {new_prog.get('name')} (ID: {prog_id})")
            else:
                # Add new program
                merged.append(new_prog)
                id_to_index[prog_id] = len(merged) - 1
                logger.info(f"Added new program: {new_prog.get('name')} (ID: {prog_id})")
        else:
            # No ID, treat as new (though this shouldn't happen with proper scrapers)
            merged.append(new_prog)
            logger.warning(f"Program missing ID, treating as new: {new_prog.get('name')}")

    return merged


def separate_active_archived(programs: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Separate programs into active and archived based on status
    """
    active = [p for p in programs if p.get("status") != "Closed"]
    archived = [p for p in programs if p.get("status") == "Closed"]
    return active, archived


def main():
    """
    Main scraping function
    """
    logger.info("Starting student program scraping process")

    # Load schema for validation
    try:
        schema = load_schema()
        logger.info("Schema loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load schema: {e}")
        sys.exit(1)

    # Load allowlist
    companies = load_allowlist()
    if not companies:
        logger.error("No companies found in allowlist")
        sys.exit(1)

    logger.info(f"Loaded {len(companies)} companies from allowlist")

    # Scrape all companies
    all_new_programs = []
    for company_config in companies:
        company_name = company_config["name"]
        logger.info(f"Processing {company_name}")

        programs = scrape_company_programs(company_config)
        all_new_programs.extend(programs)

    logger.info(f"Scraped total of {len(all_new_programs)} programs from all companies")

    # Get project root
    project_root = get_project_root()

    # Load existing programs
    active_path = os.path.join(project_root, "data", "active", "programs.json")
    archived_path = os.path.join(project_root, "data", "archived", "programs.json")

    existing_active = load_existing_programs(active_path)
    existing_archived = load_existing_programs(archived_path)
    existing_all = existing_active + existing_archived

    logger.info(
        f"Loaded {len(existing_active)} existing active programs and {len(existing_archived)} existing archived programs"
    )

    # Merge new programs with existing ones
    all_merged_programs = merge_programs(existing_all, all_new_programs)

    # Separate into active and archived
    new_active, new_archived = separate_active_archived(all_merged_programs)

    logger.info(
        f"After merging: {len(new_active)} active programs, {len(new_archived)} archived programs"
    )

    # Validate the merged data
    logger.info("Validating merged active programs...")
    active_errors = validate_programs(new_active, schema)
    logger.info("Validating merged archived programs...")
    archived_errors = validate_programs(new_archived, schema)

    if active_errors:
        logger.error(f"Validation failed for active programs: {len(active_errors)} errors")
        for error in active_errors[:5]:  # Show first 5 errors
            logger.error(f"  - {error}")
        # Don't exit here - we might still want to save what we have
    else:
        logger.info("Active programs validation passed")

    if archived_errors:
        logger.error(f"Validation failed for archived programs: {len(archived_errors)} errors")
        for error in archived_errors[:5]:  # Show first 5 errors
            logger.error(f"  - {error}")
        # Don't exit here - we might still want to save what we have
    else:
        logger.info("Archived programs validation passed")

    if active_errors or archived_errors:
        logger.error("Validation failed; refusing to overwrite catalog data")
        return 1

    # Save the updated data
    save_programs(active_path, new_active)
    save_programs(archived_path, new_archived)

    # README generation is handled by the workflow calling generate_dashboard.py

    logger.info("Scraping process completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
