#!/usr/bin/env python3
"""
Dashboard README generator for Student Program Radar Catalog
Generates the main README.md with discover-first layout
"""

import json
import os
from collections import Counter
from datetime import datetime


def get_project_root() -> str:
    """Get the project root directory"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root (since script is in scripts/ directory)
    return os.path.dirname(script_dir)


def load_programs(filepath: str) -> list[dict]:
    """Load programs from JSON file"""
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return []

    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {filepath}: {e}")
        return []
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []


def get_all_programs() -> list[dict]:
    """Get all programs from active and archived datasets"""
    project_root = get_project_root()
    active_programs = load_programs(os.path.join(project_root, "data", "active", "programs.json"))
    archived_programs = load_programs(
        os.path.join(project_root, "data", "archived", "programs.json")
    )
    return active_programs + archived_programs


def format_status_indicator(status: str) -> str:
    """Return emoji indicator for program status"""
    status_map = {
        "Accepting": "\u2705",  # ✅
        "Rolling": "\U0001f7e1",  # 🟡
        "Cohort upcoming": "\U0001f535",  # 🔵
        "Closed": "\U0001f534",  # 🔴
        "Unknown": "\u26aa",  # ⚪
    }
    return status_map.get(status, "\u26aa")


def get_apply_markdown(apply_url: str, assets_path: str = "assets/apply.svg") -> str:
    """Generate markdown for Apply cell: badge image linked to URL, or text link if badge missing"""
    project_root = get_project_root()
    asset_fs_path = os.path.join(project_root, assets_path.replace("/", os.sep))
    if os.path.exists(asset_fs_path):
        return f"[![Apply]({assets_path})]({apply_url})"
    return f"[Apply]({apply_url})"


def generate_readme_header() -> str:
    """Generate the README header: title and one-line pitch"""
    return """# Student Program Radar Catalog

A canonical, versioned, fully public catalog of student-facing non-internship programs open to U.S. college students.

"""


def generate_role_type_jump_links(programs: list[dict]) -> str:
    """Generate jump links by role_type with counts"""
    # Filter out Closed programs
    active_programs = [p for p in programs if p.get("status") != "Closed"]
    if not active_programs:
        return ""

    # Count by role_type
    role_type_counts = Counter(p.get("role_type", "Other") for p in active_programs)
    # Sort role_types alphabetically for consistent ordering
    sorted_role_types = sorted(role_type_counts.items())

    lines = []
    for role_type, count in sorted_role_types:
        # Create an anchor: lowercase, replace spaces with hyphens, remove special chars
        anchor = role_type.lower().replace(" ", "-").replace("/", "-")
        # Remove any non-alphanumeric or hyphen characters (though our role_types are clean)
        anchor = "".join(c if c.isalnum() or c == "-" else "" for c in anchor)
        lines.append(f"- [{role_type} ({count})](#{anchor})")

    return "\n".join(
        [
            "## Program Categories",
            "",
            *lines,
            "",
            "",
        ]
    )


def generate_program_tables(programs: list[dict]) -> str:
    """Generate program tables grouped by role_type"""
    # Filter out Closed programs
    active_programs = [p for p in programs if p.get("status") != "Closed"]
    if not active_programs:
        return ""

    # Group by role_type
    programs_by_role_type = {}
    for program in active_programs:
        role_type = program.get("role_type", "Other")
        programs_by_role_type.setdefault(role_type, []).append(program)

    # Sort role_types alphabetically for consistent ordering
    sorted_role_types = sorted(programs_by_role_type.keys())

    # Status priority for sorting within each table
    status_priority = {
        "Accepting": 0,
        "Rolling": 1,
        "Cohort upcoming": 2,
        "Unknown": 3,
        # Closed should not appear, but if it does, put it last
        "Closed": 4,
    }

    sections = []
    for role_type in sorted_role_types:
        role_type_programs = programs_by_role_type[role_type]
        # Sort by status priority, then by company name, then by program name
        role_type_programs.sort(
            key=lambda p: (
                status_priority.get(p.get("status", "Unknown"), 999),
                p.get("company", "Unknown"),
                p.get("name", "Unknown"),
            )
        )

        lines = [
            f"## {role_type}",
            "",
            "| Company | Program | Status | Comp | Location | Apply |",
            "|---------|---------|--------|------|----------|-------|",
        ]

        for program in role_type_programs:
            company = program.get("company", "Unknown")
            name = program.get("name", "Unknown")
            status = program.get("status", "Unknown")
            compensation = program.get("compensation_bucket", "Unknown")
            location = program.get("location_notes", "Unknown")
            apply_url = program.get("apply_url", "#")

            status_indicator = format_status_indicator(status)
            apply_markdown = get_apply_markdown(apply_url)

            lines.append(
                f"| {company} | {name} | {status_indicator} {status} | {compensation} | {location} | {apply_markdown} |"
            )

        sections.append("\n".join(lines))

    return "\n\n".join(sections) + "\n\n"


def generate_compact_stats(programs: list[dict]) -> str:
    """Generate compact statistics section"""
    active_programs = [p for p in programs if p.get("status") != "Closed"]
    total_programs = len(active_programs)
    if total_programs == 0:
        return ""

    accepting_programs = len([p for p in active_programs if p.get("status") == "Accepting"])
    rolling_programs = len([p for p in active_programs if p.get("status") == "Rolling"])
    cohort_upcoming = len([p for p in active_programs if p.get("status") == "Cohort upcoming"])

    # Calculate acceptance rate (Accepting / Total)
    acceptance_rate = (accepting_programs / total_programs * 100) if total_programs > 0 else 0

    # Average days since last verification (for active programs that have a date)
    total_days_since = 0
    verified_count = 0
    for program in active_programs:
        last_verified = program.get("last_verified")
        if last_verified:
            try:
                last_date = datetime.strptime(last_verified, "%Y-%m-%d")
                days_since = (datetime.now() - last_date).days
                total_days_since += days_since
                verified_count += 1
            except ValueError:
                pass
    avg_days_since = total_days_since / verified_count if verified_count > 0 else 0

    lines = [
        "## Repository Stats",
        "",
        f"- **Active Programs:** {total_programs}",
        f"- **Accepting Applications:** {accepting_programs}",
        f"- **Rolling Admissions:** {rolling_programs}",
        f"- **Cohort Upcoming:** {cohort_upcoming}",
        f"- **Acceptance Rate:** {acceptance_rate:.1f}%",
        f"- **Avg Days Since Verification:** {avg_days_since:.0f} days",
        "",
        "",
    ]
    return "\n".join(lines)


def generate_automation_health_strip() -> str:
    """Generate a health strip without inventing unavailable sweep telemetry."""
    return (
        "**Automation Health**: Last sweep: unavailable | "
        "Updated: unavailable | Failed scrapers: unavailable\n\n"
    )


def generate_quick_start() -> str:
    """Generate the Quick Start section"""
    return """## Quick Start

```bash
git clone https://github.com/BrianLiDesign/student-program-radar-catalog.git
cd student-program-radar-catalog
python -m venv .venv
python -m pip install -r requirements.txt
python scripts/test_end_to_end.py
python scripts/validate_data.py
```

Run `python scripts/scrape_programs.py` to refresh catalog data, then `python scripts/generate_dashboard.py` to regenerate this README.

"""


def generate_documentation_links() -> str:
    """Generate the Documentation section"""
    return """## Documentation

- [Data Schema](docs/SCHEMA.md) - Detailed schema definition
- [Status Semantics](docs/STATUS.md) - How to interpret program statuses
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the catalog
- [Development Guide](docs/DEVELOPMENT.md) - Local setup and testing
- [Automation Documentation](AUTOMATION.md) - How the automation works
- [Data Dictionary](DATA_DICTIONARY.md) - Field definitions and examples
- [Roadmap](docs/ROADMAP.md) - Planned improvements
- [Support](SUPPORT.md) - How to get help

"""


def generate_footer() -> str:
    """Generate the footer: Data Access, License, Last Updated"""
    return """## Data Access

The canonical data is available in:
- `data/active/programs.json` - Currently active programs
- `data/archived/programs.json` - Archived programs (not deleted for historical reference)

## License

This repository uses a dual license. See [NOTICE](NOTICE) for details.

- **Dataset** (`data/`): [Creative Commons Attribution 4.0 International](LICENSE) (CC-BY 4.0)
- **Code** (scripts, config, tests, docs, automation): [MIT License](LICENSE-CODE)

## Last Updated

*Last updated: {date} by automated sweep process*
""".format(date=datetime.now().strftime("%Y-%m-%d"))


def generate_readme() -> str:
    """Generate the complete README content"""
    programs = get_all_programs()
    print(f"Loaded {len(programs)} total programs")

    readme = (
        generate_readme_header()
        + generate_role_type_jump_links(programs)
        + generate_program_tables(programs)
        + generate_compact_stats(programs)
        + generate_automation_health_strip()
        + generate_quick_start()
        + generate_documentation_links()
        + generate_footer()
    )

    return readme


def main():
    """Main function to generate and write README"""
    readme_content = generate_readme()

    # Write to README.md
    project_root = get_project_root()
    readme_path = os.path.join(project_root, "README.md")

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"README.md generated successfully at {readme_path}")
    print(f"Total programs processed: {len(get_all_programs())}")


if __name__ == "__main__":
    main()
