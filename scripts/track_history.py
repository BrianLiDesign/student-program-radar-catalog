"""
Historical tracking system for student programs
Tracks changes to programs over time and maintains changelog
"""

import hashlib
import json
import logging
import os
from copy import deepcopy
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ProgramHistoryTracker:
    """Tracks changes to program records over time"""

    def __init__(self, history_dir="data/historical"):
        self.history_dir = history_dir
        self.changelog_file = os.path.join(history_dir, "changelog.json")
        self.snapshots_dir = os.path.join(history_dir, "snapshots")

        # Ensure directories exist
        os.makedirs(self.history_dir, exist_ok=True)
        os.makedirs(self.snapshots_dir, exist_ok=True)

        # Initialize changelog if it doesn't exist
        if not os.path.exists(self.changelog_file):
            self._init_changelog()

    def _init_changelog(self):
        """Initialize an empty changelog"""
        changelog = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_entries": 0,
            },
            "entries": [],
        }
        self._save_changelog(changelog)

    def _load_changelog(self):
        """Load the changelog from file"""
        try:
            with open(self.changelog_file, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._init_changelog()
            return self._load_changelog()

    def _save_changelog(self, changelog):
        """Save the changelog to file"""
        changelog["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.changelog_file, "w", encoding="utf-8") as f:
            json.dump(changelog, f, indent=2, ensure_ascii=False)

    def _compute_record_hash(self, record):
        """Compute a hash of a program record for change detection"""
        # Create a copy without volatile fields for comparison
        comparison_dict = deepcopy(record)
        # Remove fields that change frequently but don't indicate semantic changes
        fields_to_ignore = ["last_verified"]  # This changes every scrape
        for field in fields_to_ignore:
            comparison_dict.pop(field, None)

        # Sort keys for consistent hashing
        json_str = json.dumps(comparison_dict, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(json_str.encode("utf-8")).hexdigest()

    def _detect_significant_changes(self, old_record, new_record):
        """
        Detect significant changes between two record versions
        Returns list of change descriptions
        """
        changes = []

        # Define fields and their significance descriptions
        field_checks = [
            ("status", "Status changed"),
            ("role_type", "Role type changed"),
            ("domain", "Domain changed"),
            ("compensation_bucket", "Compensation changed"),
            ("school_restricted", "School restriction changed"),
        ]

        for field, description in field_checks:
            old_val = old_record.get(field)
            new_val = new_record.get(field)
            if old_val != new_val:
                changes.append(f"{description}: {old_val} → {new_val}")

        # Check for date changes in deadlines
        if "deadlines" in old_record and "deadlines" in new_record:
            date_fields = ["application", "program_start", "program_end"]
            for date_field in date_fields:
                old_date = old_record.get("deadlines", {}).get(date_field)
                new_date = new_record.get("deadlines", {}).get(date_field)
                if old_date != new_date and old_date and new_date:
                    changes.append(f"Deadline changed ({date_field}): {old_date} → {new_date}")

        # Check for significant text changes (using simple similarity)
        text_fields = ["short_description", "eligibility_summary", "location_notes"]
        for field in text_fields:
            old_val = old_record.get(field, "")
            new_val = new_record.get(field, "")
            if old_val and new_val:
                # Simple similarity check - if changed significantly, consider it
                from difflib import SequenceMatcher

                similarity = SequenceMatcher(None, old_val.lower(), new_val.lower()).ratio()
                if similarity < 0.8:  # More than 20% change
                    changes.append(f"Significant change in {field} (similarity: {similarity:.2f})")

        return changes

    def record_snapshot(self, programs, source="scraper_run"):
        """
        Record a snapshot of current programs state
        Returns snapshot metadata
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y%m%d_%H%M%S")

        # Create snapshot filename
        snapshot_filename = f"programs_snapshot_{date_str}.json"
        snapshot_path = os.path.join(self.snapshots_dir, snapshot_filename)

        # Save snapshot
        snapshot_data = {
            "metadata": {
                "timestamp": timestamp.isoformat(),
                "source": source,
                "program_count": len(programs),
                "snapshot_file": snapshot_filename,
            },
            "programs": programs,
        }

        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved snapshot: {snapshot_path}")

        # Compare with previous snapshot if exists
        changes = self._compare_with_previous_snapshot(programs, snapshot_path)

        # Record changes in changelog
        if changes:
            self._record_changes(changes, source, timestamp)

        return {
            "snapshot_path": snapshot_path,
            "timestamp": timestamp.isoformat(),
            "program_count": len(programs),
            "changes_detected": len(changes),
        }

    def _compare_with_previous_snapshot(self, current_programs, current_snapshot_path):
        """
        Compare current programs with the most recent previous snapshot
        Returns list of changes
        """
        # Get list of snapshot files sorted by time (newest first)
        snapshot_files = []
        for f in os.listdir(self.snapshots_dir):
            if f.startswith("programs_snapshot_") and f.endswith(".json"):
                # Extract timestamp from filename for sorting
                try:
                    timestamp_str = f[
                        18:-5
                    ]  # Remove "programs_snapshot_" prefix and ".json" suffix
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    snapshot_files.append((timestamp, f))
                except ValueError:
                    # Skip files that don't match the expected format
                    continue

        # Sort by timestamp (newest first)
        snapshot_files.sort(key=lambda x: x[0], reverse=True)

        # Skip the current snapshot if it's the most recent
        if len(snapshot_files) > 0:
            most_recent_time, most_recent_file = snapshot_files[0]
            most_recent_path = os.path.join(self.snapshots_dir, most_recent_file)

            # If this is the same file we just created, look at the second most recent
            if most_recent_path == current_snapshot_path and len(snapshot_files) > 1:
                _, second_recent_file = snapshot_files[1]
                most_recent_path = os.path.join(self.snapshots_dir, second_recent_file)
            elif most_recent_path == current_snapshot_path:
                # No previous snapshot to compare with
                return []
        else:
            # No previous snapshots
            return []

        try:
            # Load previous snapshot
            with open(most_recent_path, encoding="utf-8") as f:
                previous_snapshot = json.load(f)

            previous_programs = previous_snapshot.get("programs", [])
            return self._compare_program_sets(previous_programs, current_programs)

        except Exception as e:
            logger.warning(f"Could not compare with previous snapshot: {e}")
            return []

    def _compare_program_sets(self, old_programs, new_programs):
        """
        Compare two sets of programs and detect changes
        Returns list of change descriptions
        """
        changes = []

        # Create lookup dictionaries by ID
        old_by_id = {p.get("id"): p for p in old_programs if p.get("id")}
        new_by_id = {p.get("id"): p for p in new_programs if p.get("id")}

        # Find added programs
        new_ids = set(new_by_id.keys())
        old_ids = set(old_by_id.keys())
        added_ids = new_ids - old_ids
        removed_ids = old_ids - new_ids
        common_ids = new_ids & old_ids

        # Record additions
        for prog_id in added_ids:
            program = new_by_id[prog_id]
            changes.append(
                {
                    "type": "added",
                    "program_id": prog_id,
                    "program_name": program.get("name", "Unknown"),
                    "company": program.get("company", "Unknown"),
                    "description": f"New program added: {program.get('name')} ({program.get('company')})",
                }
            )

        # Record removals
        for prog_id in removed_ids:
            program = old_by_id[prog_id]
            changes.append(
                {
                    "type": "removed",
                    "program_id": prog_id,
                    "program_name": program.get("name", "Unknown"),
                    "company": program.get("company", "Unknown"),
                    "description": f"Program removed: {program.get('name')} ({program.get('company')})",
                }
            )

        # Check for modifications in common programs
        for prog_id in common_ids:
            old_program = old_by_id[prog_id]
            new_program = new_by_id[prog_id]

            # Check if significant changes occurred
            significant_changes = self._detect_significant_changes(old_program, new_program)
            if significant_changes:
                changes.append(
                    {
                        "type": "modified",
                        "program_id": prog_id,
                        "program_name": old_program.get("name", "Unknown"),
                        "company": old_program.get("company", "Unknown"),
                        "changes": significant_changes,
                        "description": f"Program modified: {old_program.get('name')} ({old_program.get('company')}) - {len(significant_changes)} changes",
                    }
                )

        return changes

    def _record_changes(self, changes, source, timestamp):
        """Record changes in the changelog"""
        changelog = self._load_changelog()

        for change in changes:
            changelog_entry = {
                "timestamp": timestamp.isoformat(),
                "source": source,
                "type": change["type"],
                "program_id": change["program_id"],
                "program_name": change["program_name"],
                "company": change["company"],
                "description": change["description"],
            }

            # Add type-specific fields
            if change["type"] == "modified":
                changelog_entry["changes"] = change.get("changes", [])

            changelog["entries"].append(changelog_entry)

        # Update metadata
        changelog["metadata"]["total_entries"] = len(changelog["entries"])
        changelog["metadata"]["last_updated"] = timestamp.isoformat()

        # Save changelog
        self._save_changelog(changelog)

        logger.info(f"Recorded {len(changes)} changes to changelog")


def track_program_changes(programs, source="scraper_run"):
    """
    Convenience function to track changes in a program set
    Returns snapshot metadata
    """
    tracker = ProgramHistoryTracker()
    return tracker.record_snapshot(programs, source)


def get_recent_changes(hours=24):
    """
    Get changes from the last N hours
    Returns list of change entries
    """
    tracker = ProgramHistoryTracker()
    changelog = tracker._load_changelog()

    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_changes = []

    for entry in changelog["entries"]:
        entry_time = datetime.fromisoformat(entry["timestamp"])
        if entry_time >= cutoff_time:
            recent_changes.append(entry)

    return sorted(recent_changes, key=lambda x: x["timestamp"], reverse=True)


def get_program_history(program_id):
    """
    Get all historical changes for a specific program
    Returns list of change entries for that program
    """
    tracker = ProgramHistoryTracker()
    changelog = tracker._load_changelog()

    program_changes = [entry for entry in changelog["entries"] if entry["program_id"] == program_id]

    return sorted(program_changes, key=lambda x: x["timestamp"])


def get_latest_snapshot():
    """
    Get the most recent snapshot of programs
    Returns snapshot data or None if no snapshots exist
    """
    tracker = ProgramHistoryTracker()

    if not os.path.exists(tracker.snapshots_dir):
        return None

    snapshot_files = []
    for f in os.listdir(tracker.snapshots_dir):
        if f.startswith("programs_snapshot_") and f.endswith(".json"):
            # Extract timestamp from filename for sorting
            try:
                timestamp_str = f[18:-5]  # Remove "programs_snapshot_" prefix and ".json" suffix
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                snapshot_files.append((timestamp, f))
            except ValueError:
                # Skip files that don't match the expected format
                continue

    if not snapshot_files:
        return None

    # Sort by timestamp (newest first)
    snapshot_files.sort(key=lambda x: x[0], reverse=True)
    most_recent_file = snapshot_files[0][1]
    most_recent_path = os.path.join(tracker.snapshots_dir, most_recent_file)

    try:
        with open(most_recent_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Could not load latest snapshot: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    print("Program History Tracker Module")
    print("==============================")

    # This would normally be called with actual program data from scrapers
    print("Module ready for use:")
    print("- track_program_changes(programs) to record a snapshot")
    print("- get_recent_changes(hours) to get recent changes")
    print("- get_program_history(program_id) to get history for a specific program")
    print("- get_latest_snapshot() to get the most recent program snapshot")
