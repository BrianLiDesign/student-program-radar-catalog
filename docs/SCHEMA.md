# Data Schema

This document describes the data schema for student program records in the Student Program Radar Catalog.

## Overview

All program records follow this JSON schema, ensuring consistency and enabling reliable consumption by the website and other tools.

## Schema Location

The canonical JSON Schema is located at: `data/schema.json`

## Core Fields

### Required Fields
These fields must be present in every program record:

- **id**: Unique identifier (UUID v5 derived from normalized `company|name`; see `scripts/program_ids.py`)
- **name**: Program name
- **company**: Company or organization offering the program
- **apply_url**: Direct URL to apply for the program
- **status**: Current status (Accepting, Rolling, Cohort upcoming, Closed, Unknown)
- **role_type**: Type of role (Ambassador, Campus Rep, Student Expert/Leader, etc.)
- **domain**: Industry domain (Tech, Design/Creative, Consumer brand, etc.)
- **eligibility_summary**: Brief summary of eligibility requirements
- **location_notes**: Location information or remote work details
- **compensation_bucket**: Compensation category (Paid, Unpaid-or-perks, Unknown)
- **last_verified**: Date when the program information was last verified
- **short_description**: Brief 1-2 sentence description of the program

### Optional/Rich Fields
These fields are included when information is available:

- **responsibilities**: List of responsibilities
- **time_commitment**: Expected time commitment
- **perks_detail**: Detailed information about perks and benefits
- **deadlines**: Object containing application/program dates
- **social_requirements**: Any social media or outreach requirements
- **source_url**: Original source URL where the program was found
- **source_snippet**: Relevant text excerpt from the source
- **school_restricted**: Whether the program is restricted to certain schools
- **notes**: Any additional notes or comments

## Status Values

See [STATUS.md](STATUS.md) for detailed definitions of each status value.

## Data Types and Formats

- **id**: String (UUID format)
- **Dates**: String in ISO 8601 format (YYYY-MM-DD)
- **URLs**: String that validates as a URI
- **Enums**: String values restricted to specific predefined options
- **Arrays**: JSON arrays of strings
- **Objects**: JSON objects with defined properties

## Example Record

```json
{
  "id": "3ba33b4a-3c1a-5555-8e1a-1a2b3c4d5e6f",
  "name": "Adobe Student Ambassador",
  "company": "Adobe",
  "apply_url": "https://www.adobe.com/education/students/ambassador.html",
  "status": "Accepting",
  "role_type": "Ambassador",
  "domain": "Tech",
  "eligibility_summary": "Full-time students at accredited universities",
  "location_notes": "Remote/virtual",
  "compensation_bucket": "Paid",
  "last_verified": "2024-01-15",
  "short_description": "Represent Adobe on campus, share your creativity, and gain professional experience.",
  "responsibilities": [
    "Host workshops and events",
    "Create content for social media",
    "Provide feedback on Adobe products"
  ],
  "time_commitment": "5-10 hours/week",
  "perks_detail": "Access to Adobe Creative Cloud, networking opportunities, stipend",
  "deadlines": {
    "application": "2024-03-01",
    "program_start": "2024-06-01",
    "program_end": "2025-05-31"
  },
  "social_requirements": "Monthly posts on social media using #AdobeAmbassador",
  "source_url": "https://www.adobe.com/education/students/ambassador.html",
  "source_snippet": "The Adobe Student Ambassador program is designed for students who are passionate about creativity and technology.",
  "school_restricted": false,
  "notes": "Program runs annually with applications opening in January"
}
```

## Validation

All data is validated against the JSON schema during the automated sweep process. Records that fail validation are logged and not included in the published datasets.

## Extensions

Future versions of the schema may add new optional fields, but required fields will never be removed to maintain backward compatibility.