# Contributing to Student Program Radar Catalog

Thank you for your interest in contributing to the Student Program Radar Catalog! This document outlines how you can help improve this public dataset of student programs.

## Current Contribution Phase

We are currently in the maintainer-managed stage, meaning:
- Only repository maintainers and the automation system can directly modify program records
- The automation system performs daily sweeps to update program information
- Manual edits to program records are not accepted via pull requests at this stage

## How You Can Contribute Now

### 1. Suggest New Programs or Corrections
- Open an issue to suggest a new program that should be included
- Report errors in existing listings (broken links, incorrect information, etc.)
- Suggest additions to the company allowlist

### 2. Add New Program Scrapers
We welcome scraper contributions for companies in the allowlist! See [AUTOMATION.md](AUTOMATION.md) for detailed instructions on:
- Creating a new scraper by inheriting from `EnhancedBaseScraper`
- Implementing `find_program_urls` and `parse_program_page`
- Registering your scraper in the scraper registry
- Testing your scraper locally before submitting a pull request

### 3. Improve Documentation
- Help improve this contributing guide
- Enhance documentation in the `/docs` directory
- Suggest improvements to the README or status documentation

### 4. Suggest Technical Improvements
- Propose enhancements to the automation system
- Suggest new data fields or improvements to the schema
- Recommend better sources for finding student programs

## Future Contribution Phases

### Phase 2: Issue-Based Suggestions
Once the automation system is stable, we will:
- Actively encourage issues suggesting new programs or corrections
- Label and triage these suggestions appropriately

### Phase 3: Validated PRs for Allowlist/Corrections
Later phases will allow:
- Verified pull requests to the company allowlist
- Corrections to specific data points (via a structured format)
- Still no direct editing of full generated records to maintain consistency

## What We Do NOT Accept

- Pull requests that directly modify program records in `/data/active/` or `/data/archived/`
- Raw scrape dumps or unprocessed data
- Changes that violate the CC-BY license
- Program suggestions without sufficient verification information

## Reporting Issues

When opening an issue, please include:

- **For new program suggestions**:
  - Program name
  - Company/organization
  - Application URL
  - Any known details about role type, domain, compensation, etc.
  - Source where you found the information

- **For corrections or issues**:
  - Specific program and what needs to be corrected
  - Evidence supporting the correction (screenshot, link, etc.)
  - Suggested fix if known

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

## Getting Started with Development

If you're interested in helping with the technical aspects of the automation system:

1. Fork this repository
2. Clone your fork locally
3. Create a new branch for your work
4. See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for setup instructions
5. Make your changes
6. Submit a pull request for review

## Questions?

If you have questions about contributing, please open an issue or contact the maintainers.

Thank you for helping make student opportunities more discoverable!
