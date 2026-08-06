# Data Dictionary

This document provides a comprehensive reference for all fields in the Student Program Radar Catalog dataset, including their definitions, data types, constraints, and examples.

## Core Fields (Required)

These fields must be present in every program record:

### id
- **Type**: String (UUID v5 format)
- **Description**: Unique identifier for the program (UUID v5 based on company+name)
- **Constraints**: Must be a valid UUID version 5
- **Example**: `"550e8400-e29b-41d4-a716-446655440000"`

### name
- **Type**: String
- **Description**: Program name
- **Constraints**: Minimum length of 1 character
- **Example**: `"Adobe Student Ambassador"`

### company
- **Type**: String
- **Description**: Company or organization offering the program
- **Constraints**: Minimum length of 1 character
- **Example**: `"Adobe"`

### apply_url
- **Type**: String (URI format)
- **Description**: Direct URL to apply for the program
- **Constraints**: Must be a valid URI
- **Example**: `"https://www.adobe.com/education/students/ambassador.html"`

### status
- **Type**: String (enum)
- **Description**: Current status of the program
- **Constraints**: Must be one of: `Accepting`, `Rolling`, `Cohort upcoming`, `Closed`, `Unknown`
- **Example`: `"Accepting"`

### role_type
- **Type**: String (enum)
- **Description**: Type of role or position
- **Constraints**: Must be one of: `Ambassador`, `Campus Rep`, `Student Expert/Leader`, `Creator/Influencer`, `Fellowship/Scholarship-adjacent`, `Organizer/Coach`, `Other`
- **Example**: `"Ambassador"`

### domain
- **Type**: String (enum)
- **Description**: Industry domain of the program
- **Constraints**: Must be one of: `Tech`, `Design/Creative`, `Consumer brand`, `Finance`, `Education/EdTech`, `Other`
- **Example**: `"Tech"`

### eligibility_summary
- **Type**: String
- **Description**: Brief summary of eligibility requirements
- **Constraints**: Minimum length of 1 character
- **Example**: `"Full-time students at accredited universities in the United States"`

### location_notes
- **Type**: String
- **Description**: Location information or remote work details
- **Constraints**: No minimum length (can be empty string)
- **Example**: `"Remote/virtual"`

### compensation_bucket
- **Type**: String (enum)
- **Description**: Compensation category
- **Constraints**: Must be one of: `Paid`, `Unpaid-or-perks`, `Unknown`
- **Example**: `"Paid"`

### last_verified
- **Type**: String (date format)
- **Description**: Date when the program information was last verified
- **Constraints**: Must be a valid date in YYYY-MM-DD format
- **Example**: `"2024-01-15"`

### short_description
- **Type**: String
- **Description**: Brief 1-2 sentence description of the program
- **Constraints**: Minimum length of 10 characters
- **Example**: `"Represent Adobe on campus, share your creativity, and gain professional experience."`

## Optional/Rich Fields

These fields are included when information is available:

### responsibilities
- **Type**: Array of strings
- **Description**: List of responsibilities
- **Constraints**: Each item must be a string
- **Example**:
  ```json
  [
    "Host workshops and events",
    "Create content for social media",
    "Provide feedback on Adobe products"
  ]
  ```

### time_commitment
- **Type**: String
- **Description**: Expected time commitment (e.g., '10 hours/week')
- **Constraints**: No specific format required, but should be descriptive
- **Example**: `"5-10 hours/week"`

### perks_detail
- **Type**: String
- **Description**: Detailed information about perks and benefits
- **Constraints**: No specific constraints
- **Example**: `"Access to Adobe Creative Cloud, networking opportunities with Adobe employees, stipend, invitation to annual summit"`

### deadlines
- **Type**: Object
- **Description**: Important dates for the program
- **Structure**:
  - `application` (string, date format): Application deadline
  - `program_start` (string, date format): Program start date
  - `program_end` (string, date format): Program end date
- **Constraints**: All dates must be in YYYY-MM-DD format if present
- **Example**:
  ```json
  {
    "application": "2024-03-01",
    "program_start": "2024-06-01",
    "program_end": "2025-05-31"
  }
  ```

### social_requirements
- **Type**: String
- **Description**: Any social media or outreach requirements
- **Constraints**: No specific constraints
- **Example**: `"Minimum 3 posts per semester on social media using #AdobeAmbassador"`

### source_url
- **Type**: String (URI format)
- **Description**: Original source URL where the program was found
- **Constraints**: Must be a valid URI
- **Example**: `"https://www.adobe.com/education/students/ambassador.html"`

### source_snippet
- **Type**: String
- **Description**: Relevant text excerpt from the source
- **Constraints**: No specific constraints
- **Example**: `"The Adobe Student Ambassador program is designed for students who are passionate about creativity and technology."`

### school_restricted
- **Type**: Boolean
- **Description**: Whether the program is restricted to certain schools
- **Constraints**: Must be true or false
- **Example**: `false`

### notes
- **Type**: String
- **Description**: Any additional notes or comments
- **Constraints**: No specific constraints
- **Example**: `"Program runs annually with applications typically opening in January"`

## Enumerated Values

### status
- `Accepting`: Currently accepting applications
- `Rolling`: Accepts applications on a rolling basis (no fixed deadline)
- `Cohort upcoming`: Applications not yet open but a future cohort is planned
- `Closed`: Not currently accepting applications
- `Unknown`: Status cannot be determined from available information

### role_type
- `Ambassador`: Represents the brand on campus and at events
- `Campus Rep`: Represents the brand specifically within a campus environment
- `Student Expert/Leader`: Shares expertise and leads peers in specific domains
- `Creator/Influencer`: Creates content and leverages social media presence
- `Fellowship/Scholarship-adjacent`: Fellowship, scholarship, or similar award-based program
- `Organizer/Coach`: Organizes events, activities, or coaches peers
- `Other`: Role type not covered by the above categories

### domain
- `Tech`: Technology companies and products
- `Design/Creative`: Design, advertising, media, and creative industries
- `Consumer brand`: Consumer goods and retail brands
- `Finance`: Banking, financial services, and fintech companies
- `Education/EdTech`: Education companies and educational technology
- `Other`: Industries not covered by the above categories

### compensation_bucket
- `Paid`: Financial compensation provided (stipend, salary, hourly wage)
- `Unpaid-or-perks`: No direct financial compensation, but may provide non-monetary benefits
- `Unknown`: Compensation information not available or not specified
