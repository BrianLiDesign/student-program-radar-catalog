#!/usr/bin/env python3
"""
End-to-end test script for Student Program Radar Catalog
Tests the full pipeline: scraping -> validation -> storage -> dashboard generation
"""

import json
import os
import shutil
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.scrapers.adobe_scraper import AdobeScraper

from generate_dashboard import generate_readme, get_project_root
from validate_data import load_programs, load_schema, validate_programs


def test_scraper_isolation():
    """Test Adobe scraper in isolation"""
    print("=== Testing Adobe Scraper in Isolation ===")

    try:
        scraper = AdobeScraper("Adobe", "https://www.adobe.com")
        programs = scraper.scrape_programs()

        print(f"[PASS] Adobe scraper found {len(programs)} programs")

        # Show first program as example
        if programs:
            print(f"  Example: {programs[0]['name']} - {programs[0]['short_description'][:50]}...")

        return programs
    except Exception as e:
        print(f"[FAIL] Adobe scraper failed: {e}")
        return []


def test_validation(programs):
    """Test validation of scraped programs"""
    print("\n=== Testing Data Validation ===")

    if not programs:
        print("[FAIL] No programs to validate")
        return False

    try:
        schema = load_schema()
        errors = validate_programs(programs, schema)

        if errors:
            print(f"[FAIL] Validation failed with {len(errors)} errors:")
            for error in errors[:3]:  # Show first 3 errors
                print(f"  - {error['program_name']}: {error['error']}")
            return False
        else:
            print("[PASS] Validation passed")
            return True
    except Exception as e:
        print(f"[FAIL] Validation error: {e}")
        return False


def test_storage(programs):
    """Test storing programs to active programs file"""
    print("\n=== Testing Data Storage ===")

    if not programs:
        print("[FAIL] No programs to store")
        return False

    try:
        project_root = get_project_root()
        active_path = os.path.join(project_root, "data", "active", "programs.json")

        # Backup original file
        backup_path = active_path + ".backup"
        if os.path.exists(active_path):
            shutil.copy2(active_path, backup_path)

        # Write test programs
        with open(active_path, "w", encoding="utf-8") as f:
            json.dump(programs, f, indent=2, ensure_ascii=False)

        # Verify file was written correctly
        loaded_programs = load_programs(active_path)
        if len(loaded_programs) == len(programs):
            print(f"[PASS] Successfully stored {len(programs)} programs to {active_path}")

            # Restore original file
            if os.path.exists(backup_path):
                shutil.move(backup_path, active_path)
                print("[PASS] Original file restored")

            return True
        else:
            print(
                f"[FAIL] Storage verification failed: expected {len(programs)}, got {len(loaded_programs)}"
            )

            # Restore original file even on failure
            if os.path.exists(backup_path):
                shutil.move(backup_path, active_path)
            return False

    except Exception as e:
        print(f"[FAIL] Storage error: {e}")
        # Try to restore backup if it exists
        backup_path = active_path + ".backup"
        if os.path.exists(backup_path):
            shutil.move(backup_path, active_path)
        return False


def test_dashboard_generation():
    """Test dashboard/README generation"""
    print("\n=== Testing Dashboard Generation ===")

    try:
        project_root = get_project_root()
        readme_path = os.path.join(project_root, "README.md")

        # Backup original README
        backup_path = readme_path + ".backup"
        if os.path.exists(readme_path):
            shutil.copy2(readme_path, backup_path)

        # Generate new README
        readme_content = generate_readme()

        # Write to temporary file first to verify
        temp_path = readme_path + ".temp"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        # Check that it looks reasonable
        if len(readme_content) > 1000 and "# Student Program Radar Catalog" in readme_content:
            print("[PASS] Dashboard generation successful")

            # Restore original README
            if os.path.exists(backup_path):
                shutil.move(backup_path, readme_path)

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return True
        else:
            print("[FAIL] Dashboard generation produced unexpected output")

            # Restore original README
            if os.path.exists(backup_path):
                shutil.move(backup_path, readme_path)

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False

    except Exception as e:
        print(f"[FAIL] Dashboard generation error: {e}")
        # Try to restore backup if it exists
        backup_path = readme_path + ".backup"
        if os.path.exists(backup_path):
            shutil.move(backup_path, readme_path)
        return False


def main():
    """Run all end-to-end tests"""
    print("Starting End-to-End Test for Student Program Radar Catalog")
    print("=" * 60)

    # Test 1: Scraper isolation
    programs = test_scraper_isolation()

    # Test 2: Validation
    validation_passed = test_validation(programs)

    # Test 3: Storage (only if we have programs and validation passed)
    storage_passed = False
    if programs and validation_passed:
        storage_passed = test_storage(programs)

    # Test 4: Dashboard generation
    dashboard_passed = test_dashboard_generation()

    # Summary
    print("\n" + "=" * 60)
    print("END-TO-END TEST SUMMARY")
    print("=" * 60)
    print(f"Scraper Isolation:     {'PASS' if programs else 'FAIL'}")
    print(f"Data Validation:       {'PASS' if validation_passed else 'FAIL'}")
    print(f"Data Storage:          {'PASS' if storage_passed else 'FAIL'}")
    print(f"Dashboard Generation:  {'PASS' if dashboard_passed else 'FAIL'}")

    all_passed = bool(programs and validation_passed and storage_passed and dashboard_passed)
    print(f"\nOverall Result:        {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
