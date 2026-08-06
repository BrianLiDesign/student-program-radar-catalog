"""
Data Quality Workflow Script
Demonstrates how to use all data quality components together:
1. Data enrichment
2. Deduplication
3. Historical tracking
4. Advanced validation
"""

import json
import os
import sys

# Add scripts directory to path
script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.insert(0, script_dir)

# Import our modules
try:
    from advanced_validation import validate_programs
    from deduplicate_programs import deduplicate_programs
    from enrich_data import batch_enrich_programs
    from track_history import track_program_changes
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    MODULES_AVAILABLE = False

def load_programs(filepath):
    """Load programs from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        return []

def save_programs(programs, filepath):
    """Save programs to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(programs, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(programs)} programs to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving to {filepath}: {e}")
        return False

def run_data_quality_workflow(input_file="data/active/programs.json",
                             output_file="data/active/programs_enriched.json",
                             enable_enrichment=True,
                             enable_deduplication=True,
                             enable_history=True,
                             enable_validation=True):
    """
    Run a complete data quality workflow
    """
    print("=" * 60)
    print("STUDENT PROGRAM RADAR CATALOG - DATA QUALITY WORKFLOW")
    print("=" * 60)

    # Step 1: Load data
    print(f"\n1. Loading data from {input_file}")
    programs = load_programs(input_file)
    if not programs:
        print("No data loaded. Exiting.")
        return False

    print(f"   Loaded {len(programs)} programs")

    # Step 2: Data enrichment
    if enable_enrichment and MODULES_AVAILABLE:
        print("\n2. Enriching program data with derived fields...")
        try:
            programs = batch_enrich_programs(programs)
            print(f"   Enriched {len(programs)} programs with derived fields")

            # Show example of enriched fields
            if programs:
                sample = programs[0]
                enriched_fields = [k for k in sample.keys() if not k.startswith('_') and k not in load_programs(input_file)[0].keys() if load_programs(input_file)]
                if enriched_fields:
                    print(f"   Example enriched fields: {', '.join(enriched_fields[:5])}{'...' if len(enriched_fields) > 5 else ''}")
        except Exception as e:
            print(f"   Error during enrichment: {e}")
            if not MODULES_AVAILABLE:
                print("   Skipping enrichment - modules not available")
    elif not MODULES_AVAILABLE:
        print("\n2. Skipping enrichment - required modules not available")

    # Step 3: Deduplication
    if enable_deduplication and MODULES_AVAILABLE:
        print("\n3. Checking for and removing duplicates...")
        try:
            deduped_programs, duplicates_info = deduplicate_programs(programs, similarity_threshold=0.85)
            removed_count = len(programs) - len(deduped_programs)
            if removed_count > 0:
                print(f"   Found and removed {removed_count} duplicate programs")
                programs = deduped_programs

                # Save duplicate info for review
                dup_file = "data/active/duplicates_found.json"
                with open(dup_file, 'w', encoding='utf-8') as f:
                    json.dump(duplicates_info, f, indent=2, ensure_ascii=False)
                print(f"   Duplicate details saved to {dup_file}")
            else:
                print("   No duplicates found")
        except Exception as e:
            print(f"   Error during deduplication: {e}")
            if not MODULES_AVAILABLE:
                print("   Skipping deduplication - modules not available")
    elif not MODULES_AVAILABLE:
        print("\n3. Skipping deduplication - required modules not available")

    # Step 4: Historical tracking
    if enable_history and MODULES_AVAILABLE:
        print("\n4. Recording historical snapshot...")
        try:
            snapshot_info = track_program_changes(programs, source="data_quality_workflow")
            print(f"   Snapshot recorded: {snapshot_info['snapshot_path']}")
            print(f"   Programs in snapshot: {snapshot_info['program_count']}")
            print(f"   Changes detected since last snapshot: {snapshot_info['changes_detected']}")
        except Exception as e:
            print(f"   Error during historical tracking: {e}")
            if not MODULES_AVAILABLE:
                print("   Skipping history tracking - modules not available")
    elif not MODULES_AVAILABLE:
        print("\n4. Skipping historical tracking - required modules not available")

    # Step 5: Advanced validation
    if enable_validation and MODULES_AVAILABLE:
        print("\n5. Running advanced validation and quality scoring...")
        try:
            validation_results = validate_programs(programs)

            print(f"   Overall Quality Score: {validation_results['overall_score']}/100")
            print(f"   Status: {validation_results['status'].upper()}")
            print(f"   Programs Analyzed: {validation_results['total_programs']}")

            if validation_results['individual_scores']:
                avg_completeness = sum(r.get('completeness_score', 0) for r in validation_results['individual_scores']) / len(validation_results['individual_scores'])
                print(f"   Average Completeness: {avg_completeness:.1f}%")

            # Show top issues
            if validation_results['batch_issues']:
                print("\n   Top Issues Found:")
                issue_counts = {}
                for issue in validation_results['batch_issues']:
                    issue_type = issue.get('type', 'unknown')
                    issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

                for issue_type, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"     - {issue_type}: {count}")

            # Show recommendations
            if validation_results['recommendations']:
                print("\n   Recommendations:")
                for i, rec in enumerate(validation_results['recommendations'][:3], 1):
                    print(f"     {i}. {rec}")

        except Exception as e:
            print(f"   Error during validation: {e}")
            if not MODULES_AVAILABLE:
                print("   Skipping validation - modules not available")
    elif not MODULES_AVAILABLE:
        print("\n5. Skipping validation - required modules not available")

    # Step 6: Save results
    print(f"\n6. Saving processed data to {output_file}")
    if save_programs(programs, output_file):
        print(f"   Successfully saved {len(programs)} programs")
    else:
        print("   Failed to save data")
        return False

    print("\n" + "=" * 60)
    print("DATA QUALITY WORKFLOW COMPLETE")
    print("=" * 60)

    return True

def main():
    """Main function to run the workflow"""
    import argparse

    parser = argparse.ArgumentParser(description='Run data quality workflow on student programs')
    parser.add_argument('--input', '-i', default='data/active/programs.json',
                        help='Input JSON file with programs')
    parser.add_argument('--output', '-o', default='data/active/programs_processed.json',
                        help='Output JSON file for processed programs')
    parser.add_argument('--skip-enrichment', action='store_true',
                        help='Skip data enrichment step')
    parser.add_argument('--skip-deduplication', action='store_true',
                        help='Skip deduplication step')
    parser.add_argument('--skip-history', action='store_true',
                        help='Skip historical tracking step')
    parser.add_argument('--skip-validation', action='store_true',
                        help='Skip validation step')
    parser.add_argument('--show-sample', action='store_true',
                        help='Show sample of processed data')

    args = parser.parse_args()

    success = run_data_quality_workflow(
        input_file=args.input,
        output_file=args.output,
        enable_enrichment=not args.skip_enrichment,
        enable_deduplication=not args.skip_deduplication,
        enable_history=not args.skip_history,
        enable_validation=not args.skip_validation
    )

    if success and args.show_sample:
        print("\nSample of processed data (first 2 programs):")
        programs = load_programs(args.output)
        if programs:
            for i, program in enumerate(programs[:2]):
                print(f"\nProgram {i+1}:")
                print(f"  ID: {program.get('id', 'N/A')}")
                print(f"  Name: {program.get('name', 'N/A')}")
                print(f"  Company: {program.get('company', 'N/A')}")
                # Show some enriched fields if available
                enriched_fields = ['program_duration_days', 'application_complexity_score', 'is_remote']
                for field in enriched_fields:
                    if field in program:
                        print(f"  {field}: {program[field]}")

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
