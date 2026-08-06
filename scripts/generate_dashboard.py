#!/usr/bin/env python3
"""
Dashboard README generator for Student Program Radar Catalog
Generates the main README.md with statistics and information
"""

import json
import os
from collections import Counter
from datetime import datetime
from typing import Dict, List


def get_project_root() -> str:
    """Get the project root directory"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root (since script is in scripts/ directory)
    return os.path.dirname(script_dir)


def load_programs(filepath: str) -> List[Dict]:
    """Load programs from JSON file"""
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {filepath}: {e}")
        return []
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []


def get_all_programs() -> List[Dict]:
    """Get all programs from active and archived datasets"""
    project_root = get_project_root()
    active_programs = load_programs(os.path.join(project_root, 'data', 'active', 'programs.json'))
    archived_programs = load_programs(os.path.join(project_root, 'data', 'archived', 'programs.json'))
    return active_programs + archived_programs


def calculate_trend_stats(programs: List[Dict]) -> Dict:
    """Calculate trend statistics: programs by month, acceptance rate, top companies"""
    # Programs by month (based on last_verified)
    programs_by_month = Counter()
    total_programs = len(programs)
    accepting_programs = 0
    company_counter = Counter()

    # For average days since last verification
    total_days_since_verification = 0
    verified_programs_count = 0

    for program in programs:
        # Count by month
        last_verified = program.get('last_verified')
        if last_verified:
            try:
                date_obj = datetime.strptime(last_verified, '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                programs_by_month[month_key] += 1

                # Calculate days since verification for average
                days_since = (datetime.now() - date_obj).days
                total_days_since_verification += days_since
                verified_programs_count += 1
            except ValueError:
                pass  # Invalid date format

        # Count accepting programs
        if program.get('status') == 'Accepting':
            accepting_programs += 1

        # Count companies
        company = program.get('company', 'Unknown')
        company_counter[company] += 1

    # Calculate acceptance rate
    acceptance_rate = (accepting_programs / total_programs * 100) if total_programs > 0 else 0

    # Calculate average days since verification
    avg_days_since_verification = (
        total_days_since_verification / verified_programs_count
        if verified_programs_count > 0 else 0
    )

    # Get top 5 companies
    top_5_companies = company_counter.most_common(5)

    return {
        'programs_by_month': dict(programs_by_month),
        'acceptance_rate': acceptance_rate,
        'top_5_companies': top_5_companies,
        'avg_days_since_verification': avg_days_since_verification
    }


def get_stale_programs(programs: List[Dict], days_threshold: int = 60) -> List[Dict]:
    """Get programs not verified in more than days_threshold days"""
    stale_programs = []
    cutoff_date = datetime.now().timestamp() - (days_threshold * 24 * 3600)

    for program in programs:
        last_verified = program.get('last_verified')
        if last_verified:
            try:
                last_date = datetime.strptime(last_verified, '%Y-%m-%d')
                if last_date.timestamp() < cutoff_date:
                    stale_programs.append(program)
            except ValueError:
                pass  # Invalid date format
        else:
            # If no last_verified date, consider it stale
            stale_programs.append(program)

    # Sort by last_verified descending (oldest first)
    stale_programs.sort(
        key=lambda x: x.get('last_verified', '1900-01-01')
    )

    return stale_programs


def format_status_indicator(status: str) -> str:
    """Return emoji indicator for program status"""
    status_map = {
        'Accepting': '🟢',
        'Rolling': '🟡',
        'Cohort upcoming': '🔵',
        'Closed': '🔴',
        'Unknown': '⚪'
    }
    return status_map.get(status, '⚪')


def format_recent_activity_table(programs: List[Dict]) -> str:
    """Format recent activity section as a compact table with max 15 rows"""
    # Get programs updated in the last 30 days
    recent_programs = []
    cutoff_date = datetime.now().timestamp() - (30 * 24 * 3600)  # 30 days ago

    for program in programs:
        last_verified = program.get('last_verified')
        if last_verified:
            try:
                last_date = datetime.strptime(last_verified, '%Y-%m-%d')
                if last_date.timestamp() > cutoff_date:
                    recent_programs.append(program)
            except ValueError:
                pass

    if not recent_programs:
        return "\n## Recently Updated Programs (Last 30 Days)\n\nNo programs updated in the last 30 days.\n"

    # Sort by last_verified descending (most recent first)
    recent_programs.sort(
        key=lambda x: x.get('last_verified', '1900-01-01'),
        reverse=True
    )

    # Take max 15 rows
    recent_programs = recent_programs[:15]

    lines = [
        "\n## Recently Updated Programs (Last 30 Days)",
        "",
        "| Program | Company | Status | Days Since Verified |",
        "|---------|---------|--------|---------------------|"
    ]

    for program in recent_programs:
        name = program.get('name', 'Unknown')
        company = program.get('company', 'Unknown')
        status = program.get('status', 'Unknown')
        last_verified = program.get('last_verified', 'Unknown')

        # Calculate days since verified
        days_since = "Unknown"
        if last_verified and last_verified != 'Unknown':
            try:
                last_date = datetime.strptime(last_verified, '%Y-%m-%d')
                days_since = str((datetime.now() - last_date).days)
            except ValueError:
                pass

        status_indicator = format_status_indicator(status)
        lines.append(f"| {name} | {company} | {status_indicator} {status} | {days_since} |")

    if len(recent_programs) == 15:
        # Check if there are more
        total_recent = len([p for p in programs if p.get('last_verified') and
                           datetime.strptime(p.get('last_verified', '1900-01-01'), '%Y-%m-%d').timestamp() >
                           (datetime.now().timestamp() - (30 * 24 * 3600))])
        if total_recent > 15:
            lines.append(f"\n*And {total_recent - 15} more...*")

    return "\n".join(lines)


def generate_readme_header() -> str:
    """Generate the README header"""
    return """# Student Program Radar Catalog

A canonical, versioned, fully public catalog of student-facing non-internship programs open to U.S. college students.

## Project Overview

This repository serves as the **source of truth** for student ambassador, campus representative, student expert/leader, creator/influencer, fellowship/scholarship-adjacent, organizer/coach, and other named student programs.

The catalog is updated via automated daily sweeps and consumed by the [student-program-radar](https://github.com/brianli808/student-program-radar) web application (and anyone else) for discovery, matching, and tracking of student opportunities.

## Quick Start

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


def generate_statistics_section(stats: Dict, trend_stats: Dict) -> str:
    """Generate the statistics section of the README"""
    lines = [
        "## Repository Statistics",
        "",
        "### Overall Counts",
        f"- **Total Programs:** {stats['total_programs']}",
        f"- **Active Programs:** {stats['active_programs']}",
        f"- **Archived Programs:** {stats['archived_programs']}",
        "",
        "### Status Breakdown (Active Programs)",
        f"- **Accepting Applications:** {stats['accepting_now']}",
        f"- **Rolling Admissions:** {stats['rolling']}",
        f"- **Cohort Upcoming:** {stats['cohort_upcoming']}",
        f"- **Status Unknown:** {stats['unknown_status']}",
        "",
        "### Advanced Statistics",
        f"- **Acceptance Rate:** {trend_stats['acceptance_rate']:.1f}% ({stats['accepting_now']}/{stats['total_programs']} programs)",
        f"- **Average Days Since Last Verification:** {trend_stats['avg_days_since_verification']:.0f} days",
        "",
        "### Programs by Month (Last Verified)",
    ]

    # Sort months chronologically (most recent first)
    sorted_months = sorted(trend_stats['programs_by_month'].items(), reverse=True)
    for month, count in sorted_months[:6]:  # Show last 6 months
        # Format month as readable date
        try:
            date_obj = datetime.strptime(month + '-01', '%Y-%m-%d')
            formatted_month = date_obj.strftime('%B %Y')
            lines.append(f"- {formatted_month}: {count} programs")
        except ValueError:
            lines.append(f"- {month}: {count} programs")

    lines.extend([
        "",
        "### Top 5 Companies by Program Count"
    ])

    for company, count in trend_stats['top_5_companies']:
        lines.append(f"- {company}: {count} programs")

    return "\n".join(lines)


def generate_stale_programs_section(stale_programs: List[Dict]) -> str:
    """Generate the programs needing verification section"""
    if not stale_programs:
        return "\n## Programs Needing Verification\n\nAll programs are up-to-date (verified within the last 60 days).\n"

    lines = [
        "\n## Programs Needing Verification",
        "",
        f"Found {len(stale_programs)} programs that haven't been verified in over 60 days:",
        "",
        "| Program | Company | Status | Last Verified | Days Since Verified |",
        "|---------|---------|--------|---------------|---------------------|"
    ]

    # Show max 10 stale programs
    display_programs = stale_programs[:10]

    for program in display_programs:
        name = program.get('name', 'Unknown')
        company = program.get('company', 'Unknown')
        status = program.get('status', 'Unknown')
        last_verified = program.get('last_verified', 'Never')

        # Calculate days since verified
        days_since = "Unknown"
        if last_verified and last_verified != 'Never':
            try:
                last_date = datetime.strptime(last_verified, '%Y-%m-%d')
                days_since = str((datetime.now() - last_date).days)
            except ValueError:
                pass

        status_indicator = format_status_indicator(status)
        lines.append(f"| {name} | {company} | {status_indicator} {status} | {last_verified} | {days_since} |")

    if len(stale_programs) > 10:
        lines.append(f"\n*And {len(stale_programs) - 10} more programs needing verification...*")

    lines.extend([
        "",
        "> 💡 **Want to help?** Contribute by verifying and updating these programs!",
        "> See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on suggesting updates.",
        "> Programs needing verification are those not checked in the last 60 days.",
        ""
    ])

    return "\n".join(lines)


def generate_documentation_links() -> str:
    """Generate links to documentation"""
    return """
## Documentation

- [Data Schema](docs/SCHEMA.md) - Detailed schema definition
- [Status Semantics](docs/STATUS.md) - How to interpret program statuses
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the catalog
- [Automation Documentation](AUTOMATION.md) - How the automation works
- [Data Dictionary](DATA_DICTIONARY.md) - Field definitions and examples

## Data Access

The canonical data is available in:
- `data/active/programs.json` - Currently active programs
- `data/archived/programs.json` - Archived programs (not deleted for historical reference)

## License

The dataset in this repository is licensed under [Creative Commons Attribution 4.0 International](LICENSE) (CC-BY).

## Last Updated

*Last updated: {date} by automated sweep process*
""".format(date=datetime.now().strftime('%Y-%m-%d'))


def generate_readme() -> str:
    """Generate the complete README content"""
    programs = get_all_programs()
    print(f"Loaded {len(programs)} total programs")

    stats = generate_statistics(programs)
    trend_stats = calculate_trend_stats(programs)
    stale_programs = get_stale_programs(programs)

    readme = generate_readme_header()
    readme += generate_statistics_section(stats, trend_stats)
    readme += format_recent_activity_table(programs)
    readme += generate_stale_programs_section(stale_programs)
    readme += generate_documentation_links()

    return readme


def generate_statistics(programs: List[Dict]) -> Dict:
    """Generate basic statistics from program data (kept for backward compatibility)"""
    stats = {
        'total_programs': len(programs),
        'active_programs': len([p for p in programs if p.get('status') != 'Closed']),
        'archived_programs': len([p for p in programs if p.get('status') == 'Closed']),
        'by_role_type': Counter(),
        'by_domain': Counter(),
        'by_compensation': Counter(),
        'by_location_type': Counter(),
        'recently_updated': 0,
        'accepting_now': 0,
        'rolling': 0,
        'cohort_upcoming': 0,
        'unknown_status': 0
    }

    # Count programs by various categories
    for program in programs:
        # Status breakdown
        status = program.get('status', 'Unknown')
        if status == 'Accepting':
            stats['accepting_now'] += 1
        elif status == 'Rolling':
            stats['rolling'] += 1
        elif status == 'Cohort upcoming':
            stats['cohort_upcoming'] += 1
        elif status == 'Unknown':
            stats['unknown_status'] += 1

        # Category breakdowns
        stats['by_role_type'][program.get('role_type', 'Other')] += 1
        stats['by_domain'][program.get('domain', 'Other')] += 1
        stats['by_compensation'][program.get('compensation_bucket', 'Unknown')] += 1

        # Location type (simplified)
        location = program.get('location_notes', '').lower()
        if 'remote' in location or 'virtual' in location:
            stats['by_location_type']['Remote'] += 1
        elif 'hybrid' in location:
            stats['by_location_type']['Hybrid'] += 1
        else:
            # Check if it contains any location info that suggests on-site
            if location and location not in ['', 'unknown', 'n/a']:
                stats['by_location_type']['On-site'] += 1
            else:
                stats['by_location_type']['Not Specified'] += 1

        # Recently updated (last 30 days)
        last_verified = program.get('last_verified')
        if last_verified:
            try:
                last_date = datetime.strptime(last_verified, '%Y-%m-%d')
                days_ago = (datetime.now() - last_date).days
                if days_ago <= 30:
                    stats['recently_updated'] += 1
            except ValueError:
                pass  # Invalid date format

    return stats


def main():
    """Main function to generate and write README"""
    readme_content = generate_readme()

    # Write to README.md
    project_root = get_project_root()
    readme_path = os.path.join(project_root, 'README.md')

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"README.md generated successfully at {readme_path}")
    print(f"Total programs processed: {len(get_all_programs())}")


if __name__ == "__main__":
    main()
