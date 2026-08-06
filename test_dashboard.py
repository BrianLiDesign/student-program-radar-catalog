"""
Unit tests for the dashboard generator.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

from scripts.generate_dashboard import (
    _asset_exists,
    format_status_indicator,
    generate_automation_health_strip,
    generate_compact_stats,
    generate_documentation_links,
    generate_program_tables,
    generate_readme_header,
    generate_role_type_jump_links,
    get_apply_markdown,
)


def test_format_status_indicator():
    """Test the status indicator emojis."""
    assert format_status_indicator("Accepting") == "\u2705"
    assert format_status_indicator("Rolling") == "\U0001f7e1"
    assert format_status_indicator("Cohort upcoming") == "\U0001f535"
    assert format_status_indicator("Closed") == "\U0001f534"
    assert format_status_indicator("Unknown") == "\u26aa"
    assert format_status_indicator("Other") == "\u26aa"


def test_get_apply_markdown():
    """Test the Apply markdown generation."""
    url = "https://example.com/apply"
    markdown = get_apply_markdown(url)
    expected = f"[![Apply](assets/apply.svg)]({url})"
    assert markdown == expected

    # Missing asset falls back to text link
    missing = get_apply_markdown(url, "assets/does-not-exist.svg")
    assert missing == f"[Apply]({url})"


def test_apply_asset_lookup_is_cached():
    """Avoid repeating the same filesystem lookup for every program row."""
    assets_path = "assets/cache-test.svg"
    _asset_exists.cache_clear()

    with patch("scripts.generate_dashboard.os.path.exists", return_value=True) as exists:
        get_apply_markdown("https://example.com/one", assets_path)
        get_apply_markdown("https://example.com/two", assets_path)

    exists.assert_called_once()


def test_generate_role_type_jump_links():
    """Test jump links generation."""
    programs = [
        {"role_type": "Ambassador", "status": "Accepting"},
        {"role_type": "Ambassador", "status": "Rolling"},
        {"role_type": "Student Expert/Leader", "status": "Unknown"},
        {"role_type": "Ambassador", "status": "Closed"},  # excluded
        {"role_type": "Creator/Influencer", "status": "Accepting"},
    ]

    jump_links = generate_role_type_jump_links(programs)
    assert "Ambassador (2)" in jump_links
    assert "Student Expert/Leader (1)" in jump_links
    assert "Creator/Influencer (1)" in jump_links
    assert "[Ambassador (2)]" in jump_links
    assert "[Student Expert/Leader (1)]" in jump_links
    assert "[Creator/Influencer (1)]" in jump_links


def test_generate_program_tables():
    """Test program tables generation."""
    programs = [
        {
            "company": "TestCo",
            "name": "Test Program",
            "status": "Accepting",
            "compensation_bucket": "Paid",
            "location_notes": "Remote",
            "apply_url": "https://example.com/apply",
            "role_type": "Ambassador",
        },
        {
            "company": "TestCo2",
            "name": "Test Program 2",
            "status": "Closed",
            "compensation_bucket": "Unpaid",
            "location_notes": "On-site",
            "apply_url": "https://example.com/apply2",
            "role_type": "Ambassador",
        },
    ]

    tables = generate_program_tables(programs)
    assert "TestCo" in tables
    assert "Test Program" in tables
    assert "\u2705 Accepting" in tables
    assert "Paid" in tables
    assert "Remote" in tables
    assert "[![Apply](assets/apply.svg)](https://example.com/apply)" in tables
    assert "| Company | Program | Status | Comp | Location | Apply |" in tables

    assert "TestCo2" not in tables
    assert "Test Program 2" not in tables


def test_generate_compact_stats():
    """Test compact statistics generation."""
    programs = [
        {"status": "Accepting"},
        {"status": "Rolling"},
        {"status": "Cohort upcoming"},
        {"status": "Unknown"},
        {"status": "Closed"},  # excluded from active programs
    ]

    past_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    programs.append({"status": "Accepting", "last_verified": past_date})
    programs.append({"status": "Rolling", "last_verified": past_date})

    stats = generate_compact_stats(programs)
    # 6 non-Closed programs
    assert "**Active Programs:** 6" in stats
    assert "**Accepting Applications:** 2" in stats
    assert "**Rolling Admissions:** 2" in stats
    assert "**Cohort Upcoming:** 1" in stats
    assert "**Acceptance Rate:** 33.3%" in stats
    assert "**Avg Days Since Verification:** 10 days" in stats


def test_generate_automation_health_strip():
    """Test that missing sweep telemetry is reported honestly."""
    health_strip = generate_automation_health_strip()
    assert "Automation Health" in health_strip
    assert "Last sweep: unavailable" in health_strip
    assert "Updated: unavailable" in health_strip
    assert "Failed scrapers: unavailable" in health_strip


def test_generate_readme_header():
    """Test the README header generation."""
    header = generate_readme_header()
    assert "# Student Program Radar Catalog" in header
    assert "A canonical, versioned, fully public catalog" in header
    assert "## Quick Start" not in header


def test_generate_documentation_links():
    """Test the documentation links generation."""
    docs = generate_documentation_links()
    assert "## Documentation" in docs
    assert "- [Data Schema](docs/SCHEMA.md)" in docs
    assert "## Data Access" not in docs
    assert "## License" not in docs
