#!/usr/bin/env python3
"""
Deduplication system for Student Program Radar Catalog
Detects and handles potential duplicate programs across sources
"""

import json
import os
import re
import sys
from collections import defaultdict
from difflib import SequenceMatcher

# Add the scripts directory to the path
script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
sys.path.insert(0, script_dir)


def load_programs(filepath):
    """Load programs from JSON file"""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def save_programs(programs, filepath):
    """Save programs to JSON file"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(programs, f, indent=2, ensure_ascii=False)


def normalize_string(s):
    """Normalize string for comparison"""
    if not s:
        return ""
    # Convert to lowercase, remove extra whitespace, remove special characters
    s = str(s).lower().strip()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def similarity_score(str1, str2):
    """Calculate similarity score between two strings"""
    if not str1 or not str2:
        return 0.0
    return SequenceMatcher(None, normalize_string(str1), normalize_string(str2)).ratio()


def are_programs_duplicate(prog1, prog2, threshold=0.8):
    """
    Determine if two programs are likely duplicates
    Returns tuple (is_duplicate, confidence_score, reason)
    """
    # Check company match first - if companies don't match, unlikely to be duplicates
    if prog1.get("company", "").lower() != prog2.get("company", "").lower():
        return False, 0.0, "Different companies"

    # Compare names
    name_similarity = similarity_score(prog1.get("name", ""), prog2.get("name", ""))

    # Compare apply URLs
    url_similarity = similarity_score(prog1.get("apply_url", ""), prog2.get("apply_url", ""))

    # Weighted scoring
    # Name similarity is most important, then URL
    combined_score = (name_similarity * 0.7) + (url_similarity * 0.3)

    # Additional checks for strong indicators
    reasons = []

    if name_similarity > 0.9:
        reasons.append("Very similar names")
    elif name_similarity > 0.7:
        reasons.append("Similar names")

    if url_similarity > 0.8:
        reasons.append("Similar application URLs")

    # Check if IDs are related (same base)
    id1 = prog1.get("id", "")
    id2 = prog2.get("id", "")
    if id1 and id2:
        # Extract potential base ID (before last hex segment)
        base1 = re.sub(r"-[0-9a-f]{12}$", "", id1) if re.search(r"-[0-9a-f]{12}$", id1) else id1
        base2 = re.sub(r"-[0-9a-f]{12}$", "", id2) if re.search(r"-[0-9a-f]{12}$", id2) else id2
        if base1 == base2 and base1 != id1:  # They share a base but have different suffixes
            reasons.append("Related IDs")
            combined_score = max(combined_score, 0.85)

    is_duplicate = combined_score >= threshold
    reason = "; ".join(reasons) if reasons else "Below threshold"

    return is_duplicate, combined_score, reason


def find_duplicates(programs, similarity_threshold=0.8):
    """
    Find potential duplicate pairs in a list of programs
    Returns list of tuples: (index1, index2, similarity_score, reason)
    """
    duplicates = []

    for i in range(len(programs)):
        for j in range(i + 1, len(programs)):
            is_dup, score, reason = are_programs_duplicate(
                programs[i], programs[j], similarity_threshold
            )
            if is_dup:
                duplicates.append((i, j, score, reason))

    return duplicates


def group_duplicates(duplicate_pairs):
    """
    Group duplicate pairs into clusters
    Returns list of sets, where each set contains indices of duplicates
    """
    # Create adjacency list
    graph = defaultdict(set)
    for i, j, _, _ in duplicate_pairs:
        graph[i].add(j)
        graph[j].add(i)

    # Find connected components
    visited = set()
    components = []

    def dfs(node, component):
        visited.add(node)
        component.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor, component)

    for node in range(len(graph)):
        if node not in visited:
            component = set()
            dfs(node, component)
            if len(component) > 1:  # Only include groups with duplicates
                components.append(component)

    return components


def select_canonical_program(programs, indices):
    """
    Select the canonical program from a group of duplicates
    Prefers:
    1. Most complete data (more filled fields)
    2. Recently verified
    3. Higher quality source
    """

    def score_program(prog):
        score = 0

        # Count filled fields (more is better)
        required_fields = [
            "id",
            "name",
            "company",
            "apply_url",
            "status",
            "role_type",
            "domain",
            "eligibility_summary",
            "location_notes",
            "compensation_bucket",
            "last_verified",
            "short_description",
        ]

        for field in required_fields:
            if prog.get(field):
                score += 1

        # Bonus for optional fields
        optional_fields = [
            "responsibilities",
            "time_commitment",
            "perks_detail",
            "deadlines",
            "social_requirements",
            "source_snippet",
        ]

        for field in optional_fields:
            if prog.get(field):
                score += 0.5

        # Prefer more recent verification
        try:
            from datetime import datetime

            last_verified = prog.get("last_verified", "1900-01-01")
            date_obj = datetime.strptime(last_verified, "%Y-%m-%d")
            # More recent dates get higher scores
            days_since = (datetime.now() - date_obj).days
            # Negative because more recent = smaller days_since = higher score when we negate
            score += max(0, (365 * 2 - days_since) / 365)  # Cap at 2 years
        except ValueError:
            pass  # If date parsing fails, skip this bonus

        return score

    # Score all programs in the group
    scored_programs = [(score_program(programs[i]), i, programs[i]) for i in indices]
    # Sort by score descending
    scored_programs.sort(reverse=True)

    # Return the highest scoring program
    return scored_programs[0][1], scored_programs[0][2]  # index, program


def deduplicate_programs(programs, similarity_threshold=0.8):
    """
    Main deduplication function
    Returns: (deduplicated_programs, duplicates_info)
    """
    print(f"Analyzing {len(programs)} programs for duplicates...")

    # Find duplicate pairs
    duplicate_pairs = find_duplicates(programs, similarity_threshold)
    print(f"Found {len(duplicate_pairs)} potential duplicate pairs")

    if not duplicate_pairs:
        return programs, []

    # Group into clusters
    duplicate_groups = group_duplicates(duplicate_pairs)
    print(f"Grouped into {len(duplicate_groups)} duplicate clusters")

    # Track which indices are duplicates
    duplicate_indices = set()
    for group in duplicate_groups:
        duplicate_indices.update(group)

    print(f"Found {len(duplicate_indices)} programs that are part of duplicate groups")

    # For each group, select canonical and mark others as duplicates
    indices_to_remove = []
    duplicates_info = []

    for group in duplicate_groups:
        group_list = list(group)
        canonical_index, canonical_program = select_canonical_program(programs, group_list)

        # Mark all others in group for removal
        for idx in group_list:
            if idx != canonical_index:
                indices_to_remove.append(idx)
                duplicates_info.append(
                    {
                        "duplicate_index": idx,
                        "duplicate_program": programs[idx],
                        "canonical_index": canonical_index,
                        "canonical_program": canonical_program,
                        "reason": "Selected as duplicate during deduplication",
                    }
                )

    # Remove duplicates (in reverse order to maintain indices)
    indices_to_remove.sort(reverse=True)
    deduplicated_programs = [
        programs[i] for i in range(len(programs)) if i not in indices_to_remove
    ]

    print(f"Removed {len(indices_to_remove)} duplicate programs")
    print(f"Remaining programs: {len(deduplicated_programs)}")

    return deduplicated_programs, duplicates_info


def main():
    """Main function to run deduplication"""
    import argparse

    parser = argparse.ArgumentParser(description="Deduplicate student programs")
    parser.add_argument(
        "--input", "-i", default="data/active/programs.json", help="Input JSON file with programs"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="data/active/programs_deduped.json",
        help="Output JSON file for deduplicated programs",
    )
    parser.add_argument(
        "--duplicates",
        "-d",
        default="data/active/duplicates.json",
        help="Output JSON file for duplicate information",
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=0.8,
        help="Similarity threshold for duplicate detection (0.0-1.0)",
    )

    args = parser.parse_args()

    # Load programs
    programs = load_programs(args.input)

    # Deduplicate
    deduped_programs, duplicates_info = deduplicate_programs(programs, args.threshold)

    # Save results
    save_programs(deduped_programs, args.output)
    with open(args.duplicates, "w", encoding="utf-8") as f:
        json.dump(duplicates_info, f, indent=2, ensure_ascii=False)

    print(f"Deduplicated programs saved to: {args.output}")
    print(f"Duplicate information saved to: {args.duplicates}")

    # Print summary
    print("\n=== DEDUPLICATION SUMMARY ===")
    print(f"Original count: {len(programs)}")
    print(f"After deduplication: {len(deduped_programs)}")
    print(f"Removed: {len(programs) - len(deduped_programs)} duplicates")
    if len(programs) > 0:
        print(f"Reduction: {((len(programs) - len(deduped_programs)) / len(programs) * 100):.1f}%")


if __name__ == "__main__":
    main()
