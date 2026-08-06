# Student Program Radar Catalog

A canonical, versioned, fully public catalog of student-facing non-internship programs open to U.S. college students.

## Program Categories

- [Ambassador (3)](#ambassador)
- [Creator/Influencer (3)](#creator-influencer)
- [Fellowship/Scholarship-adjacent (1)](#fellowship-scholarship-adjacent)
- [Organizer/Coach (1)](#organizer-coach)
- [Other (3)](#other)
- [Student Expert/Leader (1)](#student-expert-leader)

## Ambassador

| Company | Program | Status | Comp | Location | Apply |
|---------|---------|--------|------|----------|-------|
| Adobe | Adobe Student Ambassador | ⚪ Unknown | Paid | Remote/virtual | [![Apply](assets/apply.svg)](https://www.adobe.com/education/students/ambassador.html) |
| Apple | Apple Education | ⚪ Unknown | Unpaid-or-perks | Campus-based (varies by location) | [![Apply](assets/apply.svg)](https://www.apple.com/education/) |
| Netflix | Netflix Campus Ambassador | ⚪ Unknown | Paid | Campus-based or remote (varies by program) | [![Apply](assets/apply.svg)](https://jobs.netflix.com/early_talent) |

## Creator/Influencer

| Company | Program | Status | Comp | Location | Apply |
|---------|---------|--------|------|----------|-------|
| Adobe | Adobe Design Circle | ⚪ Unknown | Unpaid-or-perks | Remote/virtual with optional regional meetups | [![Apply](assets/apply.svg)](https://www.adobe.com/education/students/design-circle.html) |
| Adobe | Adobe Ideapalooza | ⚪ Unknown | Unpaid-or-perks | Virtual competition | [![Apply](assets/apply.svg)](https://www.adobe.com/education/students/ideapalooza.html) |
| Microsoft | Microsoft Imagine Cup | ⚪ Unknown | Unpaid-or-perks | Virtual competition with regional finals and world championship | [![Apply](assets/apply.svg)](https://www.microsoft.com/en-us/imaginecup/) |

## Fellowship/Scholarship-adjacent

| Company | Program | Status | Comp | Location | Apply |
|---------|---------|--------|------|----------|-------|
| Adobe | Adobe Creative Cloud Fellowship | ⚪ Unknown | Paid | Hybrid - virtual meetings with annual summit in San Francisco | [![Apply](assets/apply.svg)](https://www.adobe.com/education/students/creative-cloud-fellowship.html) |

## Organizer/Coach

| Company | Program | Status | Comp | Location | Apply |
|---------|---------|--------|------|----------|-------|
| Adobe | Adobe University Outreach | ⚪ Unknown | Unpaid-or-perks | Campus-based (various locations) | [![Apply](assets/apply.svg)](https://www.adobe.com/education/students/university-outreach.html) |

## Other

| Company | Program | Status | Comp | Location | Apply |
|---------|---------|--------|------|----------|-------|
| Microsoft | Microsoft Garage Internship | ⚪ Unknown | Paid | Hybrid - Remote work with optional Redmond, WA headquarters visits | [![Apply](assets/apply.svg)](https://www.microsoft.com/en-us/garage/students/) |
| Microsoft | Microsoft LEAP Apprenticeship Program | ⚪ Unknown | Paid | Hybrid - Multiple US locations including Redmond, Atlanta, Chicago | [![Apply](assets/apply.svg)](https://www.microsoft.com/en-us/leap) |
| Microsoft | Microsoft University Recruiting Programs | ⚪ Unknown | Paid | Varies by program - multiple locations worldwide | [![Apply](assets/apply.svg)](https://www.microsoft.com/en-us/university) |

## Student Expert/Leader

| Company | Program | Status | Comp | Location | Apply |
|---------|---------|--------|------|----------|-------|
| Microsoft | Microsoft Learn Student Ambassador | ⚪ Unknown | Unpaid-or-perks | Hybrid - virtual with optional local events | [![Apply](assets/apply.svg)](https://learn.microsoft.com/en-us/training/studentambassadors/) |

## Repository Stats

- **Active Programs:** 12
- **Accepting Applications:** 0
- **Rolling Admissions:** 0
- **Cohort Upcoming:** 0
- **Acceptance Rate:** 0.0%
- **Avg Days Since Verification:** 890 days

**Automation Health**: Last sweep: unavailable | Updated: unavailable | Failed scrapers: unavailable

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

## Documentation

- [Data Schema](docs/SCHEMA.md) - Detailed schema definition
- [Status Semantics](docs/STATUS.md) - How to interpret program statuses
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the catalog
- [Development Guide](docs/DEVELOPMENT.md) - Local setup and testing
- [Automation Documentation](AUTOMATION.md) - How the automation works
- [Data Dictionary](DATA_DICTIONARY.md) - Field definitions and examples
- [Roadmap](docs/ROADMAP.md) - Planned improvements
- [Support](SUPPORT.md) - How to get help

## Data Access

The canonical data is available in:
- `data/active/programs.json` - Currently active programs
- `data/archived/programs.json` - Archived programs (not deleted for historical reference)

## License

This repository uses a dual license. See [NOTICE](NOTICE) for details.

- **Dataset** (`data/`): [Creative Commons Attribution 4.0 International](LICENSE) (CC-BY 4.0)
- **Code** (scripts, config, tests, docs, automation): [MIT License](LICENSE-CODE)

## Last Updated

*Last updated: 2026-08-05 by automated sweep process*
