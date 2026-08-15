# Student Program Radar Catalog

A canonical, versioned, fully public catalog of student-facing non-internship programs open to U.S. college students.

## Program Categories

- [Ambassador (1)](#ambassador)
- [Creator/Influencer (1)](#creator-influencer)
- [Fellowship/Scholarship-adjacent (14)](#fellowship-scholarship-adjacent)
- [Other (1)](#other)
- [Student Expert/Leader (3)](#student-expert-leader)

## Ambassador

| Company | Program | Status | Comp | Location | Apply |
|---------|---------|--------|------|----------|-------|
| Adobe | Adobe Student Ambassador | ✅ Accepting | Unpaid-or-perks | Campus-based with virtual components | [![Apply](assets/apply.svg)](https://www.adobeforeducation.com/student-ambassador-program) |

## Creator/Influencer

| Company | Program | Status | Comp | Location | Apply |
|---------|---------|--------|------|----------|-------|
| Microsoft | Microsoft Imagine Cup | ⚪ Unknown | Unpaid-or-perks | Global / varies by program | [![Apply](assets/apply.svg)](https://imaginecup.microsoft.com/en-us) |

## Fellowship/Scholarship-adjacent

| Company | Program | Status | Comp | Location | Apply |
|---------|---------|--------|------|----------|-------|
| JetBrains | JetBrains Academy for Students | ✅ Accepting | Unpaid-or-perks | Online / global | [![Apply](assets/apply.svg)](https://hyperskill.org/projects/324?track=79) |
| AMD | AMD University Program | ⚪ Unknown | Unpaid-or-perks | Global (online resources) | [![Apply](assets/apply.svg)](https://www.amd.com/en/corporate/university-program.html) |
| Arm | Arm Education | ⚪ Unknown | Unpaid-or-perks | Online / global | [![Apply](assets/apply.svg)](https://learn.arm.com/?icid=devhub:developer:all-pages:nav-link) |
| Canva | Canva for Education | ⚪ Unknown | Unpaid-or-perks | Global (online) | [![Apply](assets/apply.svg)](https://www.canva.com/edu-signup/) |
| Coursera | Coursera for Campus | ⚪ Unknown | Unpaid-or-perks | Online / global | [![Apply](assets/apply.svg)](https://www.coursera.org/campus/learn-more) |
| Databricks | Databricks Academy | ⚪ Unknown | Unpaid-or-perks | Online / global | [![Apply](assets/apply.svg)](https://www.databricks.com/training/catalog/get-started-with-databricks-for-machine-learning-2461) |
| Elastic | Elastic Training | ⚪ Unknown | Unpaid-or-perks | Online / global | [![Apply](assets/apply.svg)](https://cloud.elastic.co/serverless-registration?pg=global&plcmt=nav&cta=205352-serverless) |
| Figma | Figma for Education | ⚪ Unknown | Unpaid-or-perks | Global (online) | [![Apply](assets/apply.svg)](https://www.figma.com/education/apply) |
| IBM | IBM SkillsBuild for University Students | ⚪ Unknown | Unpaid-or-perks | Online / global | [![Apply](assets/apply.svg)](https://skillsbuild.org/sign-up) |
| MongoDB | MongoDB for Students | ⚪ Unknown | Unpaid-or-perks | Online / global | [![Apply](assets/apply.svg)](https://www.mongodb.com/cloud/atlas/register) |
| NVIDIA | NVIDIA Training for Students | ⚪ Unknown | Unpaid-or-perks | Online / global | [![Apply](assets/apply.svg)](https://www.nvidia.com/en-us/startups/) |
| Notion | Notion for Education | ⚪ Unknown | Unpaid-or-perks | Global (online) | [![Apply](assets/apply.svg)](https://www.notion.com/help/notion-for-education) |
| Salesforce | Salesforce Student Program | ⚪ Unknown | Unpaid-or-perks | Online / global | [![Apply](assets/apply.svg)](https://trailheadacademy.salesforce.com/) |
| Unity | Unity Education | ⚪ Unknown | Unpaid-or-perks | Global (online) | [![Apply](assets/apply.svg)](https://learn.unity.com/educators) |

## Other

| Company | Program | Status | Comp | Location | Apply |
|---------|---------|--------|------|----------|-------|
| Microsoft | Microsoft LEAP Apprenticeship Program | ⚪ Unknown | Unpaid-or-perks | Global / varies by program | [![Apply](assets/apply.svg)](https://leap.microsoft.com/en-US/) |

## Student Expert/Leader

| Company | Program | Status | Comp | Location | Apply |
|---------|---------|--------|------|----------|-------|
| GitHub | GitHub Campus Expert | ⚪ Unknown | Unpaid-or-perks | Global (virtual with local events) | [![Apply](assets/apply.svg)](https://github.com/education/students/campus-expert) |
| Google | Google Developer Groups on Campus Lead | ⚪ Unknown | Unpaid-or-perks | Campus-based (global program) | [![Apply](assets/apply.svg)](https://app.advocu.com/gdg/join) |
| Microsoft | Microsoft Learn Student Ambassador | ⚪ Unknown | Unpaid-or-perks | Global / varies by program | [![Apply](assets/apply.svg)](https://mvp.microsoft.com/studentambassadors) |

## Repository Stats

- **Active Programs:** 20
- **Accepting Applications:** 2
- **Rolling Admissions:** 0
- **Cohort Upcoming:** 0
- **Acceptance Rate:** 10.0%
- **Avg Days Since Verification:** 0 days

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

Run `python scripts/scrape_programs.py` to refresh catalog data and regenerate this README.

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

*Last updated: 2026-08-14 by automated sweep process*
