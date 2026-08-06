# Student Program Radar Catalog

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

## Repository Statistics

### Overall Counts
- **Total Programs:** 12
- **Active Programs:** 12
- **Archived Programs:** 0

### Status Breakdown (Active Programs)
- **Accepting Applications:** 0
- **Rolling Admissions:** 0
- **Cohort Upcoming:** 0
- **Status Unknown:** 12

### Advanced Statistics
- **Acceptance Rate:** 0.0% (0/12 programs)
- **Average Days Since Last Verification:** 890 days

### Programs by Month (Last Verified)
- August 2024: 2 programs
- February 2024: 3 programs
- January 2024: 7 programs

### Top 5 Companies by Program Count
- Adobe: 5 programs
- Microsoft: 5 programs
- Apple: 1 programs
- Netflix: 1 programs
## Recently Updated Programs (Last 30 Days)

No programs updated in the last 30 days.

## Programs Needing Verification

Found 12 programs that haven't been verified in over 60 days:

| Program | Company | Status | Last Verified | Days Since Verified |
|---------|---------|--------|---------------|---------------------|
| Microsoft Imagine Cup | Microsoft | ⚪ Unknown | 2024-01-10 | 938 |
| Adobe Student Ambassador | Adobe | ⚪ Unknown | 2024-01-15 | 933 |
| Microsoft Learn Student Ambassador | Microsoft | ⚪ Unknown | 2024-01-20 | 928 |
| Adobe Design Circle | Adobe | ⚪ Unknown | 2024-01-20 | 928 |
| Adobe University Outreach | Adobe | ⚪ Unknown | 2024-01-25 | 923 |
| Adobe Ideapalooza | Adobe | ⚪ Unknown | 2024-01-30 | 918 |
| Microsoft LEAP Apprenticeship Program | Microsoft | ⚪ Unknown | 2024-01-30 | 918 |
| Adobe Creative Cloud Fellowship | Adobe | ⚪ Unknown | 2024-02-01 | 916 |
| Microsoft Garage Internship | Microsoft | ⚪ Unknown | 2024-02-01 | 916 |
| Microsoft University Recruiting Programs | Microsoft | ⚪ Unknown | 2024-02-15 | 902 |

*And 2 more programs needing verification...*

> 💡 **Want to help?** Contribute by verifying and updating these programs!
> See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on suggesting updates.
> Programs needing verification are those not checked in the last 60 days.

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

*Last updated: 2026-08-05 by automated sweep process*
