#!/usr/bin/env python3
"""
Data validation script for Student Program Radar Catalog
Validates program data against the JSON schema and generates data quality reports
"""

import json
import os
import sys
from collections import defaultdict

from jsonschema import ValidationError, validate


def load_schema():
    """Load the JSON schema from file"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root, then to data/schema.json
    schema_path = os.path.join(script_dir, '..', 'data', 'schema.json')
    schema_path = os.path.normpath(schema_path)
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_programs(filepath):
    """Load programs from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_programs(programs, schema):
    """Validate a list of programs against the schema"""
    errors = []
    for i, program in enumerate(programs):
        try:
            validate(instance=program, schema=schema)
        except ValidationError as e:
            errors.append({
                'index': i,
                'program_id': program.get('id', 'NO_ID'),
                'program_name': program.get('name', 'UNKNOWN'),
                'error': str(e)
            })
    return errors

def generate_data_quality_report(programs, report_type="programs"):
    """Generate a data quality report for the given programs"""
    print(f"\n=== DATA QUALITY REPORT FOR {report_type.upper()} ===")

    total_programs = len(programs)
    if total_programs == 0:
        print("No programs to analyze.")
        return

    # Initialize counters
    stats = {
        'total': total_programs,
        'missing_id': 0,
        'missing_name': 0,
        'missing_company': 0,
        'missing_apply_url': 0,
        'missing_status': 0,
        'missing_role_type': 0,
        'missing_domain': 0,
        'missing_eligibility_summary': 0,
        'missing_location_notes': 0,
        'missing_compensation_bucket': 0,
        'missing_last_verified': 0,
        'missing_short_description': 0,
        'missing_responsibilities': 0,
        'missing_time_commitment': 0,
        'missing_perks_detail': 0,
        'missing_deadlines': 0,
        'missing_social_requirements': 0,
        'missing_source_snippet': 0,
        'status_distribution': defaultdict(int),
        'role_type_distribution': defaultdict(int),
        'domain_distribution': defaultdict(int),
        'compensation_distribution': defaultdict(int),
        'missing_required_fields': []  # Track which required fields are missing
    }

    required_fields = [
        'id', 'name', 'company', 'apply_url', 'status', 'role_type',
        'domain', 'eligibility_summary', 'location_notes', 'compensation_bucket',
        'last_verified', 'short_description'
    ]

    # Analyze each program
    for i, program in enumerate(programs):
        missing_fields = []

        # Check required fields
        for field in required_fields:
            if not program.get(field):
                stats[f'missing_{field}'] += 1
                missing_fields.append(field)

        # Check optional/common fields
        if not program.get('responsibilities'):
            stats['missing_responsibilities'] += 1
        if not program.get('time_commitment'):
            stats['missing_time_commitment'] += 1
        if not program.get('perks_detail'):
            stats['missing_perks_detail'] += 1
        if not program.get('deadlines'):
            stats['missing_deadlines'] += 1
        if not program.get('social_requirements'):
            stats['missing_social_requirements'] += 1
        if not program.get('source_snippet'):
            stats['missing_source_snippet'] += 1

        # Track distributions
        stats['status_distribution'][program.get('status', 'Unknown')] += 1
        stats['role_type_distribution'][program.get('role_type', 'Unknown')] += 1
        stats['domain_distribution'][program.get('domain', 'Unknown')] += 1
        stats['compensation_distribution'][program.get('compensation_bucket', 'Unknown')] += 1

        # If any required fields are missing, track the program
        if missing_fields:
            stats['missing_required_fields'].append({
                'index': i,
                'program_id': program.get('id', 'NO_ID'),
                'program_name': program.get('name', 'UNKNOWN'),
                'missing_fields': missing_fields
            })

    # Print summary statistics
    print(f"Total Programs Analyzed: {stats['total']}")

    print("\n--- Missing Required Fields ---")
    for field in required_fields:
        count = stats[f'missing_{field}']
        percentage = (count / total_programs) * 100 if total_programs > 0 else 0
        print(f"  {field}: {count} ({percentage:.1f}%)")

    print("\n--- Missing Optional/Common Fields ---")
    optional_fields = [
        ('responsibilities', 'Responsibilities'),
        ('time_commitment', 'Time Commitment'),
        ('perks_detail', 'Perks Detail'),
        ('deadlines', 'Deadlines'),
        ('social_requirements', 'Social Requirements'),
        ('source_snippet', 'Source Snippet')
    ]

    for field, label in optional_fields:
        count = stats[f'missing_{field}']
        percentage = (count / total_programs) * 100 if total_programs > 0 else 0
        print(f"  {label}: {count} ({percentage:.1f}%)")

    print("\n--- Field Distribution ---")
    print("  Status Distribution:")
    for status, count in sorted(stats['status_distribution'].items()):
        percentage = (count / total_programs) * 100
        print(f"    {status}: {count} ({percentage:.1f}%)")

    print("  Role Type Distribution:")
    for role_type, count in sorted(stats['role_type_distribution'].items()):
        percentage = (count / total_programs) * 100
        print(f"    {role_type}: {count} ({percentage:.1f}%)")

    print("  Domain Distribution:")
    for domain, count in sorted(stats['domain_distribution'].items()):
        percentage = (count / total_programs) * 100
        print(f"    {domain}: {count} ({percentage:.1f}%)")

    print("  Compensation Distribution:")
    for compensation, count in sorted(stats['compensation_distribution'].items()):
        percentage = (count / total_programs) * 100
        print(f"    {compensation}: {count} ({percentage:.1f}%)")

    # Print worst offenders if any
    if stats['missing_required_fields']:
        print(f"\n--- Programs with Missing Required Fields ({len(stats['missing_required_fields'])} total) ---")
        # Show first 5 problematic programs
        for prog in stats['missing_required_fields'][:5]:
            print(f"  - {prog['program_name']} (ID: {prog['program_id']})")
            print(f"    Missing: {', '.join(prog['missing_fields'])}")
        if len(stats['missing_required_fields']) > 5:
            print(f"    ... and {len(stats['missing_required_fields']) - 5} more")

    # Calculate completeness score
    total_required_fields = len(required_fields) * total_programs
    missing_required_count = sum(stats[f'missing_{field}'] for field in required_fields)
    completeness_score = ((total_required_fields - missing_required_count) / total_required_fields) * 100 if total_required_fields > 0 else 0

    print("\n--- DATA COMPLETENESS SCORE ---")
    print(f"  Overall Completeness: {completeness_score:.1f}%")

    if completeness_score >= 90:
        print("  Rating: Excellent")
    elif completeness_score >= 80:
        print("  Rating: Good")
    elif completeness_score >= 70:
        print("  Rating: Fair")
    else:
        print("  Rating: Needs Improvement")

def main():
    """Main validation function"""
    print("Loading schema...")
    schema = load_schema()

    # Get project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # Validate active programs
    active_path = os.path.join(project_root, 'data', 'active', 'programs.json')
    print(f"Validating active programs from {active_path}...")
    active_programs = load_programs(active_path)
    active_errors = validate_programs(active_programs, schema)

    # Validate archived programs
    archived_path = os.path.join(project_root, 'data', 'archived', 'programs.json')
    print(f"Validating archived programs from {archived_path}...")
    archived_programs = load_programs(archived_path)
    archived_errors = validate_programs(archived_programs, schema)

    # Report validation results
    print("\n=== VALIDATION RESULTS ===")
    print(f"Active programs: {len(active_programs)} total")
    print(f"Archived programs: {len(archived_programs)} total")

    if active_errors:
        print(f"\n[FAIL] Active programs validation FAILED with {len(active_errors)} errors:")
        for error in active_errors:
            print(f"  - Index {error['index']} (ID: {error['program_id']}, Name: {error['program_name']})")
            print(f"    {error['error']}")
    else:
        print("\n[PASS] Active programs validation PASSED")

    if archived_errors:
        print(f"\n[FAIL] Archived programs validation FAILED with {len(archived_errors)} errors:")
        for error in archived_errors:
            print(f"  - Index {error['index']} (ID: {error['program_id']}, Name: {error['program_name']})")
            print(f"    {error['error']}")
    else:
        print("\n[PASS] Archived programs validation PASSED")

    # Generate data quality reports
    generate_data_quality_report(active_programs, "Active Programs")
    generate_data_quality_report(archived_programs, "Archived Programs")

    # Exit with error code if any validation failed
    if active_errors or archived_errors:
        print("\n[ERROR] VALIDATION FAILED")
        sys.exit(1)
    else:
        print("\n[SUCCESS] ALL VALIDATIONS PASSED")
        sys.exit(0)

if __name__ == "__main__":
    main()