"""
Advanced validation system for student programs
Implements cross-program validation, temporal validation, consistency checks,
and data quality scoring for comprehensive data integrity assessment
"""

import logging
import re
import statistics
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class AdvancedDataValidator:
    """Advanced validation system for program data quality"""

    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.historical_data = []  # Would be loaded from database in production
        self.industry_benchmarks = self._load_industry_benchmarks()

    def _load_validation_rules(self) -> dict:
        """Load validation rules configuration"""
        return {
            "compensation_ranges": {
                "Paid": {"min_stipend": 0, "max_stipend": 10000},  # Monthly stipend in USD
                "Unpaid-or-perks": {"max_stipend": 500},  # Small stipends only
                "Unknown": {"min_stipend": 0, "max_stipend": 5000},
            },
            "time_commitment_bounds": {"min_hours": 0, "max_hours": 80},  # Per week
            "program_duration_bounds": {"min_days": 1, "max_days": 730},  # 1 day to 2 years
            "text_field_min_lengths": {"short_description": 10, "eligibility_summary": 10},
            "required_completion_rates": {
                "high_priority": ["id", "name", "company", "apply_url", "status"],
                "medium_priority": ["role_type", "domain", "compensation_bucket"],
                "low_priority": ["time_commitment", "perks_detail"],
            },
        }

    def _load_industry_benchmarks(self) -> dict:
        """Load industry benchmark data for comparison"""
        # In a real implementation, this would come from a database or external source
        return {
            "average_program_duration_days": 180,  # ~6 months
            "common_role_types": [
                "Ambassador",
                "Student Expert/Leader",
                "Creator/Influencer",
                "Fellowship/Scholarship-adjacent",
            ],
            "common_domains": ["Tech", "Design/Creative", "Consumer brand"],
            "typical_compensation_distribution": {
                "Paid": 0.4,
                "Unpaid-or-perks": 0.5,
                "Unknown": 0.1,
            },
        }

    def validate_program_batch(self, programs: list[dict]) -> dict[str, Any]:
        """
        Run comprehensive validation on a batch of programs
        Returns validation results with scores and detailed feedback
        """
        if not programs:
            return {
                "overall_score": 0,
                "status": "error",
                "message": "No programs to validate",
                "individual_scores": [],
                "batch_issues": [],
                "recommendations": [],
            }

        # Validate each program individually
        individual_results = []
        batch_issues = []

        for i, program in enumerate(programs):
            result = self.validate_single_program(program, index=i)
            individual_results.append(result)

            # Collect batch-level issues from individual validions
            if result.get("issues"):
                for issue in result["issues"]:
                    issue["program_index"] = i
                    issue["program_id"] = program.get("id", f"UNKNOWN_{i}")
                    batch_issues.append(issue)

        # Run cross-program validations
        cross_program_issues = self._run_cross_validations(programs)
        batch_issues.extend(cross_program_issues)

        # Calculate batch-level statistics
        batch_stats = self._calculate_batch_statistics(programs)

        # Compute overall quality score
        individual_scores = [r.get("quality_score", 0) for r in individual_results]
        avg_individual_score = statistics.mean(individual_scores) if individual_scores else 0

        # Factor in cross-program consistency
        consistency_bonus = self._calculate_consistency_bonus(programs, cross_program_issues)
        base_score = min(100, avg_individual_score + consistency_bonus)

        # Determine status
        if base_score >= 90:
            status = "excellent"
        elif base_score >= 75:
            status = "good"
        elif base_score >= 60:
            status = "fair"
        else:
            status = "needs_improvement"

        # Generate recommendations
        recommendations = self._generate_recommendations(
            individual_results, batch_issues, batch_stats
        )

        return {
            "overall_score": round(base_score, 1),
            "status": status,
            "total_programs": len(programs),
            "average_individual_score": round(avg_individual_score, 1),
            "consistency_bonus": round(consistency_bonus, 1),
            "individual_scores": individual_results,
            "batch_issues": batch_issues,
            "batch_statistics": batch_stats,
            "recommendations": recommendations,
            "validation_timestamp": datetime.now().isoformat(),
        }

    def validate_single_program(self, program: dict, index: int = None) -> dict[str, Any]:
        """
        Validate a single program and return detailed results
        """
        issues = []
        warnings = []
        strengths = []

        # 1. Basic schema validation (would normally use jsonschema)
        schema_issues = self._validate_basic_schema(program)
        issues.extend(
            [{"type": "schema", "field": field, "message": msg} for field, msg in schema_issues]
        )

        # 2. Data type and format validation
        type_issues = self._validate_data_types(program)
        issues.extend(
            [{"type": "data_type", "field": field, "message": msg} for field, msg in type_issues]
        )

        # 3. Business logic validation
        logic_issues = self._validate_business_logic(program)
        issues.extend(
            [
                {"type": "business_logic", "field": field, "message": msg}
                for field, msg in logic_issues
            ]
        )

        # 4. Temporal validation
        temporal_issues = self._validate_temporal_consistency(program)
        issues.extend(
            [{"type": "temporal", "field": field, "message": msg} for field, msg in temporal_issues]
        )

        # 5. Content quality validation
        content_issues = self._validate_content_quality(program)
        issues.extend(
            [
                {"type": "content_quality", "field": field, "message": msg}
                for field, msg in content_issues
            ]
        )

        # 6. Completeness check
        completeness_score = self._calculate_completeness_score(program)
        if completeness_score < 70:
            issues.append(
                {
                    "type": "completeness",
                    "field": "overall",
                    "message": f"Low completeness score: {completeness_score:.1f}%",
                }
            )

        # Calculate field-specific scores
        field_scores = self._calculate_field_scores(program)

        # Overall quality score (0-100)
        # Weighted combination of different validation aspects
        weights = {
            "schema_compliance": 0.25,
            "data_types": 0.15,
            "business_logic": 0.20,
            "temporal_consistency": 0.15,
            "content_quality": 0.15,
            "completeness": 0.10,
        }

        # Calculate component scores
        schema_score = 100 - (len([i for i in issues if i["type"] == "schema"]) * 10)
        type_score = 100 - (len([i for i in issues if i["type"] == "data_type"]) * 10)
        logic_score = 100 - (len([i for i in issues if i["type"] == "business_logic"]) * 10)
        temporal_score = 100 - (len([i for i in issues if i["type"] == "temporal"]) * 10)
        content_score = 100 - (len([i for i in issues if i["type"] == "content_quality"]) * 10)
        completeness_score_norm = completeness_score  # Already 0-100

        # Ensure scores don't go below 0
        component_scores = {
            "schema_compliance": max(0, min(100, schema_score)),
            "data_types": max(0, min(100, type_score)),
            "business_logic": max(0, min(100, logic_score)),
            "temporal_consistency": max(0, min(100, temporal_score)),
            "content_quality": max(0, min(100, content_score)),
            "completeness": max(0, min(100, completeness_score_norm)),
        }

        # Calculate weighted average
        quality_score = sum(component_scores[key] * weights[key] for key in weights)

        # Determine status for this program
        if quality_score >= 90:
            program_status = "excellent"
        elif quality_score >= 75:
            program_status = "good"
        elif quality_score >= 60:
            program_status = "fair"
        else:
            program_status = "poor"

        return {
            "index": index,
            "program_id": program.get("id", "UNKNOWN"),
            "program_name": program.get("name", "Unknown"),
            "quality_score": round(quality_score, 1),
            "status": program_status,
            "component_scores": {k: round(v, 1) for k, v in component_scores.items()},
            "field_scores": {k: round(v, 1) for k, v in field_scores.items()},
            "issues": issues,
            "warnings": warnings,
            "strengths": strengths,
            "completeness_score": round(completeness_score, 1),
        }

    def _validate_basic_schema(self, program: dict) -> list[tuple]:
        """Validate basic schema requirements"""
        issues = []

        # Required fields from the original schema
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
            value = program.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                issues.append((field, f"Required field '{field}' is missing or empty"))

        # Validate ID format (should be UUID-like)
        program_id = program.get("id")
        if program_id and isinstance(program_id, str):
            uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
            if not re.match(uuid_pattern, program_id, re.IGNORECASE):
                issues.append(("id", f"ID '{program_id}' doesn't match expected UUID format"))

        # Validate URL format
        apply_url = program.get("apply_url")
        if apply_url and isinstance(apply_url, str):
            if not re.match(r"^https?://[^\s/$.?#].[^\s]*$", apply_url):
                issues.append(("apply_url", f"URL '{apply_url}' doesn't appear to be valid"))

        # Validate date format
        last_verified = program.get("last_verified")
        if last_verified and isinstance(last_verified, str):
            try:
                datetime.strptime(last_verified, "%Y-%m-%d")
            except ValueError:
                issues.append(
                    ("last_verified", f"Date '{last_verified}' is not in YYYY-MM-DD format")
                )

        return issues

    def _validate_data_types(self, program: dict) -> list[tuple]:
        """Validate data types of fields"""
        issues = []

        # Define expected types
        type_expectations = {
            "id": str,
            "name": str,
            "company": str,
            "apply_url": str,
            "status": str,
            "role_type": str,
            "domain": str,
            "eligibility_summary": str,
            "location_notes": str,
            "compensation_bucket": str,
            "last_verified": str,
            "short_description": str,
            "responsibilities": list,
            "time_commitment": str,
            "perks_detail": str,
            "social_requirements": str,
            "source_url": str,
            "source_snippet": str,
            "school_restricted": bool,
            "notes": str,
        }

        for field, expected_type in type_expectations.items():
            value = program.get(field)
            # Only check if field exists and is not None
            if value is not None and not isinstance(value, expected_type):
                issues.append(
                    (
                        field,
                        f"Field '{field}' expected {expected_type.__name__}, got {type(value).__name__}",
                    )
                )

        # Special handling for deadlines (should be dict if present)
        deadlines = program.get("deadlines")
        if deadlines is not None and not isinstance(deadlines, dict):
            issues.append(
                ("deadlines", f"Field 'deadlines' expected dict, got {type(deadlines).__name__}")
            )

        return issues

    @staticmethod
    def _extract_hours_per_week(time_commitment: str):
        """Return a representative weekly hour value when one is stated."""
        if not re.search(r"\b(?:hours?|hrs?)\b", time_commitment, re.IGNORECASE):
            return None

        values = [float(value) for value in re.findall(r"\d+(?:\.\d+)?", time_commitment)]
        if not values:
            return None
        if len(values) >= 2 and re.search(r"\d\s*[-–]\s*\d", time_commitment):
            return sum(values[:2]) / 2
        return values[0]

    def _validate_business_logic(self, program: dict) -> list[tuple]:
        """Validate business logic rules"""
        issues = []

        # Compensation consistency
        compensation = program.get("compensation_bucket")
        if compensation in self.validation_rules["compensation_ranges"]:
            # Note: We'd need to parse stipend from perks_details or similar for real validation
            # For now, we'll check logical consistency
            if compensation == "Unpaid-or-perks":
                perks = program.get("perks_detail", "").lower()
                # If claiming unpaid but mentioning significant stipend, flag for review
                stipend_indicators = ["$", "stipend", "pay", "salary", "compensation", "paid"]
                if any(indicator in perks for indicator in stipend_indicators):
                    # This isn't necessarily an error, but worth noting
                    pass  # In a real system, this might be a warning rather than error

        # Time commitment reasonableness
        time_commitment = program.get("time_commitment")
        if time_commitment and isinstance(time_commitment, str):
            hours = self._extract_hours_per_week(time_commitment)
            if hours is not None:
                bounds = self.validation_rules["time_commitment_bounds"]
                if hours < bounds["min_hours"] or hours > bounds["max_hours"]:
                    issues.append(
                        (
                            "time_commitment",
                            f"Time commitment '{time_commitment}' ({hours} hrs/week) outside reasonable bounds "
                            f"[{bounds['min_hours']}-{bounds['max_hours']}]",
                        )
                    )

        # Status consistency with dates
        status = program.get("status")
        deadlines = program.get("deadlines", {})
        if isinstance(deadlines, dict):
            end_date_str = deadlines.get("program_end")
            if end_date_str and status != "Closed":
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                    if end_date < datetime.now():
                        # Program ended but status isn't Closed
                        issues.append(
                            (
                                "status",
                                f"Program end date ({end_date_str}) is past but status is '{status}'",
                            )
                        )
                except ValueError:
                    pass  # Date parsing error caught elsewhere

        return issues

    def _validate_temporal_consistency(self, program: dict) -> list[tuple]:
        """Validate temporal consistency of dates"""
        issues = []

        deadlines = program.get("deadlines", {})
        if not isinstance(deadlines, dict):
            return issues  # Type error caught elsewhere

        date_fields = ["application", "program_start", "program_end"]
        dates = {}

        # Parse all valid dates
        for field in date_fields:
            date_str = deadlines.get(field)
            if date_str and isinstance(date_str, str):
                try:
                    dates[field] = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    issues.append((f"deadlines.{field}", f"Invalid date format: {date_str}"))

        # Check logical ordering
        if "program_start" in dates and "program_end" in dates:
            if dates["program_start"] > dates["program_end"]:
                issues.append(("deadlines", "Program start date is after end date"))

        if "application" in dates and "program_start" in dates:
            # Application deadline should typically be before program start
            # But allow for rolling admissions or late applications
            if dates["application"] > dates["program_start"]:
                days_diff = (dates["application"] - dates["program_start"]).days
                if days_diff > 30:  # More than a month after start seems unusual
                    issues.append(
                        (
                            "deadlines",
                            f"Application deadline ({deadlines.get('application')}) is "
                            f"{days_diff} days after program start date",
                        )
                    )

        # Check if dates are too far in the future/past
        now = datetime.now()
        for field, date_obj in dates.items():
            if date_obj > now + timedelta(days=730):  # More than 2 years in future
                issues.append(
                    (
                        f"deadlines.{field}",
                        f"Date is more than 2 years in future: {date_obj.strftime('%Y-%m-%d')}",
                    )
                )
            elif date_obj < now - timedelta(days=730):  # More than 2 years in past
                issues.append(
                    (
                        f"deadlines.{field}",
                        f"Date is more than 2 years in past: {date_obj.strftime('%Y-%m-%d')}",
                    )
                )

        return issues

    def _validate_content_quality(self, program: dict) -> list[tuple]:
        """Validate content quality and completeness"""
        issues = []

        # Check for placeholder or template text
        placeholder_indicators = [
            "todo",
            "tbd",
            "placeholder",
            "example",
            "sample",
            "lorem ipsum",
            "description here",
            "text goes here",
            "to be determined",
            "coming soon",
        ]

        text_fields = [
            "name",
            "short_description",
            "eligibility_summary",
            "location_notes",
            "perks_detail",
            "social_requirements",
        ]

        for field in text_fields:
            value = program.get(field)
            if isinstance(value, str):
                lower_value = value.lower()
                for indicator in placeholder_indicators:
                    if indicator in lower_value:
                        issues.append(
                            (field, f"Content appears to contain placeholder text: '{indicator}'")
                        )

        # Check for overly short meaningful fields
        min_lengths = self.validation_rules["text_field_min_lengths"]
        for field, min_length in min_lengths.items():
            value = program.get(field)
            if isinstance(value, str) and len(value.strip()) < min_length:
                issues.append(
                    (
                        field,
                        f"Field too short: {len(value.strip())} characters (minimum {min_length})",
                    )
                )

        # Check responsibilities quality
        responsibilities = program.get("responsibilities", [])
        if isinstance(responsibilities, list):
            if len(responsibilities) == 0:
                issues.append(("responsibilities", "Responsibilities list is empty"))
            elif len(responsibilities) < 2:
                issues.append(
                    (
                        "responsibilities",
                        f"Only {len(responsibilities)} responsibility listed (consider more detail)",
                    )
                )

            # Check for generic/plausible responsibilities
            generic_responses = [
                "participate in activities",
                "attend meetings",
                "complete tasks",
                "help with projects",
                "support team",
                "other duties as assigned",
            ]

            generic_count = 0
            for resp in responsibilities:
                if isinstance(resp, str):
                    resp_lower = resp.lower().strip()
                    for generic in generic_responses:
                        if generic in resp_lower:
                            generic_count += 1
                            break

            if len(responsibilities) > 0 and (generic_count / len(responsibilities)) > 0.5:
                issues.append(
                    ("responsibilities", "More than 50% of responsibilities appear generic")
                )

        # Check perks detail quality
        perks = program.get("perks_detail", "")
        if isinstance(perks, str):
            if len(perks.strip()) < 10:
                issues.append(("perks_detail", "Perks description is very brief"))
            elif "no perks" in perks.lower() or "none" in perks.lower():
                # This might be valid, but worth noting
                pass

        return issues

    def _calculate_completeness_score(self, program: dict) -> float:
        """Calculate completeness percentage for a program"""
        # Define field importance weights
        field_weights = {
            # Critical fields (must have)
            "id": 5,
            "name": 5,
            "company": 5,
            "apply_url": 5,
            # Important fields (should have)
            "status": 4,
            "role_type": 4,
            "domain": 4,
            "eligibility_summary": 4,
            "location_notes": 4,
            "compensation_bucket": 4,
            "last_verified": 4,
            "short_description": 4,
            # Valuable fields (nice to have)
            "responsibilities": 3,
            "time_commitment": 3,
            "perks_detail": 3,
            "deadlines": 3,
            "social_requirements": 3,
            # Supplementary fields
            "source_url": 2,
            "source_snippet": 2,
            "school_restricted": 2,
            "notes": 2,
        }

        total_possible = sum(field_weights.values())
        earned_points = 0

        for field, weight in field_weights.items():
            value = program.get(field)

            # Check if field has meaningful content
            has_content = False
            if value is not None:
                if isinstance(value, str):
                    has_content = bool(value.strip())
                elif isinstance(value, list):
                    has_content = len(value) > 0
                elif isinstance(value, dict):
                    has_content = len(value) > 0
                elif isinstance(value, bool):  # school_restricted is boolean
                    has_content = True  # Boolean values are always meaningful
                else:
                    has_content = True  # For other types, assume meaningful if not None

            if has_content:
                earned_points += weight

        # Special handling for deadlines - check if meaningful subfields exist
        if "deadlines" in program and isinstance(program["deadlines"], dict):
            deadlines = program["deadlines"]
            meaningful_deadline_fields = sum(
                1
                for v in deadlines.values()
                if v is not None and (isinstance(v, str) and v.strip())
            )
            if meaningful_deadline_fields > 0:
                # Already counted in the weight above, but could give bonus for completeness
                pass

        if total_possible > 0:
            return (earned_points / total_possible) * 100
        else:
            return 0.0

    def _calculate_field_scores(self, program: dict) -> dict[str, float]:
        """Calculate individual field quality scores"""
        scores = {}

        # This would implement more sophisticated field-level scoring
        # For now, return basic completeness per field
        fields_to_check = [
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
            "responsibilities",
            "time_commitment",
            "perks_detail",
            "deadlines",
            "social_requirements",
            "source_url",
            "source_snippet",
            "school_restricted",
            "notes",
        ]

        for field in fields_to_check:
            value = program.get(field)
            if value is None:
                scores[field] = 0.0
            elif isinstance(value, str):
                scores[field] = 100.0 if value.strip() else 0.0
            elif isinstance(value, list):
                scores[field] = 100.0 if len(value) > 0 else 0.0
            elif isinstance(value, dict):
                scores[field] = 100.0 if len(value) > 0 else 0.0
            elif isinstance(value, bool):
                scores[field] = 100.0  # Boolean is always valid
            else:
                scores[field] = 100.0  # Assume other types are valid if not None

        return scores

    def _run_cross_validations(self, programs: list[dict]) -> list[dict]:
        """Run validations that compare programs across the batch"""
        issues = []

        if len(programs) < 2:
            return issues  # Need at least 2 programs for cross-validation

        # 1. Duplicate detection (similar to deduplication system)
        duplicates = self._find_potential_duplicates(programs)
        for dup_pair in duplicates:
            issues.append(
                {
                    "type": "potential_duplicate",
                    "program1_index": dup_pair[0],
                    "program2_index": dup_pair[1],
                    "program1_id": programs[dup_pair[0]].get("id", "UNKNOWN"),
                    "program2_id": programs[dup_pair[1]].get("id", "UNKNOWN"),
                    "similarity_score": dup_pair[2],
                    "message": f"Potential duplicate detected (similarity: {dup_pair[2]:.2f})",
                }
            )

        # 2. Statistical outlier detection
        outliers = self._detect_statistical_outliers(programs)
        for outlier in outliers:
            issues.append(
                {
                    "type": "statistical_outlier",
                    "program_index": outlier["index"],
                    "program_id": outlier["program_id"],
                    "field": outlier["field"],
                    "value": outlier["value"],
                    "expected_range": outlier["expected_range"],
                    "message": f"Field '{outlier['field']}' value {outlier['value']} is outside expected range {outlier['expected_range']}",
                }
            )

        # 3. Consistency checks for similar programs from same company
        consistency_issues = self._check_company_consistency(programs)
        issues.extend(consistency_issues)

        return issues

    def _find_potential_duplicates(
        self, programs: list[dict], threshold: float = 0.85
    ) -> list[tuple[int, int, float]]:
        """Find potential duplicate pairs in the program list"""
        from difflib import SequenceMatcher

        def similarity(s1, s2):
            if not s1 or not s2:
                return 0.0
            return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

        duplicates = []
        n = len(programs)

        for i in range(n):
            for j in range(i + 1, n):
                prog1, prog2 = programs[i], programs[j]

                # Quick company check first
                if prog1.get("company", "").lower() != prog2.get("company", "").lower():
                    continue

                # Compare names
                name_sim = similarity(prog1.get("name", ""), prog2.get("name", ""))

                # Compare apply URLs
                url_sim = similarity(prog1.get("apply_url", ""), prog2.get("apply_url", ""))

                # Combined score
                combined_score = (name_sim * 0.7) + (url_sim * 0.3)

                if combined_score >= threshold:
                    duplicates.append((i, j, combined_score))

        return duplicates

    def _detect_statistical_outliers(self, programs: list[dict]) -> list[dict]:
        """Detect statistical outliers in numerical fields"""
        outliers = []

        # Program duration from enriched data
        durations = []
        for i, prog in enumerate(programs):
            duration_days = prog.get("program_duration_days")
            if duration_days is not None and isinstance(duration_days, (int, float)):
                durations.append((i, duration_days))

        if len(durations) >= 4:  # Need enough samples for meaningful stats
            values = [d[1] for d in durations]
            try:
                mean_val = statistics.mean(values)
                stdev_val = statistics.stdev(values) if len(values) > 1 else 0

                # Define outlier as > 2 standard deviations from mean
                threshold = 2 * stdev_val if stdev_val > 0 else float("inf")

                for idx, val in durations:
                    if abs(val - mean_val) > threshold:
                        outliers.append(
                            {
                                "index": idx,
                                "program_id": programs[idx].get("id", "UNKNOWN"),
                                "field": "program_duration_days",
                                "value": val,
                                "expected_range": f"{mean_val - 2 * stdev_val:.1f} to {mean_val + 2 * stdev_val:.1f} days",
                                "deviation": f"{((val - mean_val) / stdev_val * 100) if stdev_val > 0 else 0:.1f}% from mean",
                            }
                        )
            except (statistics.StatisticsError, ZeroDivisionError):
                pass  # Not enough variation or other statistical issue

        # Application complexity scores
        complexity_scores = []
        for i, prog in enumerate(programs):
            score = prog.get("application_complexity_score")
            if score is not None and isinstance(score, (int, float)):
                complexity_scores.append((i, score))

        if len(complexity_scores) >= 4:
            values = [s[1] for s in complexity_scores]
            try:
                mean_val = statistics.mean(values)
                stdev_val = statistics.stdev(values) if len(values) > 1 else 0
                threshold = 2 * stdev_val if stdev_val > 0 else float("inf")

                for idx, val in complexity_scores:
                    if abs(val - mean_val) > threshold:
                        outliers.append(
                            {
                                "index": idx,
                                "program_id": programs[idx].get("id", "UNKNOWN"),
                                "field": "application_complexity_score",
                                "value": val,
                                "expected_range": f"{max(0, mean_val - 2 * stdev_val):.1f} to {min(100, mean_val + 2 * stdev_val):.1f}",
                                "deviation": f"{((val - mean_val) / stdev_val * 100) if stdev_val > 0 else 0:.1f}% from mean",
                            }
                        )
            except (statistics.StatisticsError, ZeroDivisionError):
                pass

        # Time commitment hours/week
        time_hours = []
        for i, prog in enumerate(programs):
            time_str = prog.get("time_commitment", "")
            hours = self._extract_hours_per_week(time_str)
            if hours is not None:
                time_hours.append((i, hours))

        if len(time_hours) >= 4:
            values = [t[1] for t in time_hours]
            try:
                mean_val = statistics.mean(values)
                stdev_val = statistics.stdev(values) if len(values) > 1 else 0
                threshold = 2 * stdev_val if stdev_val > 0 else float("inf")

                for idx, val in time_hours:
                    if abs(val - mean_val) > threshold:
                        outliers.append(
                            {
                                "index": idx,
                                "program_id": programs[idx].get("id", "UNKNOWN"),
                                "field": "time_commitment_hours_per_week",
                                "value": val,
                                "expected_range": f"{max(0, mean_val - 2 * stdev_val):.1f} to {mean_val + 2 * stdev_val:.1f} hrs/week",
                                "deviation": f"{((val - mean_val) / stdev_val * 100) if stdev_val > 0 else 0:.1f}% from mean",
                            }
                        )
            except (statistics.StatisticsError, ZeroDivisionError):
                pass

        return outliers

    def _check_company_consistency(self, programs: list[dict]) -> list[dict]:
        """Check for inconsistencies among programs from the same company"""
        issues = []

        # Group programs by company
        companies = {}
        for i, prog in enumerate(programs):
            company = prog.get("company", "").strip()
            if company:
                if company not in companies:
                    companies[company] = []
                companies[company].append((i, prog))

        # Check each company's programs for consistency
        for company, prog_list in companies.items():
            if len(prog_list) < 2:
                continue  # Need at least 2 programs to compare

            # Check for inconsistent compensation within same company
            compensation_values = [
                p[1].get("compensation_bucket")
                for p in prog_list
                if p[1].get("compensation_bucket")
            ]
            if len(set(compensation_values)) > 2:  # Allow some variation but not too much
                # This could be legitimate (internships vs fellowships), so flag as warning rather than error
                pass

            # Check for wildly different program durations from same company
            durations = []
            for idx, prog in prog_list:
                duration = prog.get("program_duration_days")
                if duration is not None:
                    durations.append((idx, duration))

            if len(durations) >= 3:
                try:
                    durations_only = [d[1] for d in durations]
                    mean_duration = statistics.mean(durations_only)
                    stdev_duration = (
                        statistics.stdev(durations_only) if len(durations_only) > 1 else 0
                    )

                    if stdev_duration > 0:
                        max_deviation = max(abs(d - mean_duration) for d in durations_only)
                        # If any program deviates more than 3 standard deviations, flag it
                        if max_deviation > 3 * stdev_duration:
                            for idx, duration in durations:
                                deviation = abs(duration - mean_duration)
                                if deviation > 2 * stdev_duration:  # Still flag notable deviations
                                    issues.append(
                                        {
                                            "type": "company_consistency",
                                            "company": company,
                                            "program_index": idx,
                                            "program_id": prog_list[
                                                next(
                                                    i
                                                    for i, (p_idx, _) in enumerate(prog_list)
                                                    if p_idx == idx
                                                )
                                            ][1].get("id", "UNKNOWN"),
                                            "field": "program_duration_days",
                                            "value": duration,
                                            "company_average": f"{mean_duration:.1f} days",
                                            "deviation": f"{((duration - mean_duration) / stdev_duration * 100) if stdev_duration > 0 else 0:.1f}% from company average",
                                            "message": f"Program duration varies significantly from other {company} programs",
                                        }
                                    )
                except (statistics.StatisticsError, ZeroDivisionError):
                    pass

        return issues

    def _calculate_consistency_bonus(
        self, programs: list[dict], cross_program_issues: list[dict]
    ) -> float:
        """Calculate bonus points for good cross-program consistency"""
        if len(programs) < 2:
            return 0.0

        # Start with perfect score and deduct for issues
        base_score = 20.0  # Maximum bonus for consistency

        # Deduct for various types of issues
        duplicate_penalty = (
            len([i for i in cross_program_issues if i.get("type") == "potential_duplicate"]) * 3
        )
        outlier_penalty = (
            len([i for i in cross_program_issues if i.get("type") == "statistical_outlier"]) * 2
        )
        consistency_penalty = (
            len([i for i in cross_program_issues if i.get("type") == "company_consistency"]) * 1.5
        )

        penalty = min(20, duplicate_penalty + outlier_penalty + consistency_penalty)  # Cap penalty
        return max(0, base_score - penalty)

    def _calculate_batch_statistics(self, programs: list[dict]) -> dict[str, Any]:
        """Calculate statistics for the entire batch"""
        if not programs:
            return {}

        stats = {
            "total_programs": len(programs),
            "companies_represented": len(
                set(p.get("company", "") for p in programs if p.get("company"))
            ),
            "status_distribution": {},
            "role_type_distribution": {},
            "domain_distribution": {},
            "compensation_distribution": {},
            "avg_completeness": 0.0,
            "date_range": {},
        }

        # Distribution counts
        statuses = [p.get("status", "Unknown") for p in programs]
        role_types = [p.get("role_type", "Unknown") for p in programs]
        domains = [p.get("domain", "Unknown") for p in programs]
        compensations = [p.get("compensation_bucket", "Unknown") for p in programs]

        for status in statuses:
            stats["status_distribution"][status] = stats["status_distribution"].get(status, 0) + 1
        for role in role_types:
            stats["role_type_distribution"][role] = stats["role_type_distribution"].get(role, 0) + 1
        for domain in domains:
            stats["domain_distribution"][domain] = stats["domain_distribution"].get(domain, 0) + 1
        for comp in compensations:
            stats["compensation_distribution"][comp] = (
                stats["compensation_distribution"].get(comp, 0) + 1
            )

        # Average completeness
        completeness_scores = [self._calculate_completeness_score(p) for p in programs]
        if completeness_scores:
            stats["avg_completeness"] = sum(completeness_scores) / len(completeness_scores)

        # Date range
        dates = [p.get("last_verified") for p in programs if p.get("last_verified")]
        if dates:
            try:
                parsed_dates = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
                stats["date_range"] = {
                    "earliest": min(parsed_dates).strftime("%Y-%m-%d"),
                    "latest": max(parsed_dates).strftime("%Y-%m-%d"),
                    "span_days": (max(parsed_dates) - min(parsed_dates)).days,
                }
            except ValueError:
                pass  # Date parsing errors handled elsewhere

        return stats

    def _generate_recommendations(
        self, individual_results: list[dict], batch_issues: list[dict], batch_stats: dict
    ) -> list[str]:
        """Generate actionable recommendations based on validation results"""
        recommendations = []

        if not individual_results:
            return ["No programs to analyze"]

        # Analyze common issues
        issue_types = {}
        for issue in batch_issues:
            issue_type = issue.get("type", "unknown")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

        # Completeness recommendations
        avg_completeness = batch_stats.get("avg_completeness", 0)
        if avg_completeness < 70:
            recommendations.append(
                f"Improve data completeness (current average: {avg_completeness:.1f}%). Focus on missing fields in {len([r for r in individual_results if r.get('completeness_score', 0) < 70])} programs."
            )

        # Schema issues
        schema_issues = issue_types.get("schema", 0)
        if schema_issues > 0:
            recommendations.append(
                f"Fix {schema_issues} schema validation errors (missing required fields or invalid formats)."
            )

        # Data type issues
        type_issues = issue_types.get("data_type", 0)
        if type_issues > 0:
            recommendations.append(
                f"Correct {type_issues} data type mismatches (e.g., strings where booleans expected)."
            )

        # Business logic issues
        logic_issues = issue_types.get("business_logic", 0)
        if logic_issues > 0:
            recommendations.append(
                f"Review {logic_issues} business logic violations (e.g., status/date inconsistencies)."
            )

        # Temporal issues
        temporal_issues = issue_types.get("temporal", 0)
        if temporal_issues > 0:
            recommendations.append(
                f"Address {temporal_issues} temporal inconsistencies (e.g., illogical date sequences)."
            )

        # Content quality issues
        content_issues = issue_types.get("content_quality", 0)
        if content_issues > 0:
            recommendations.append(
                f"Improve {content_issues} content quality issues (e.g., placeholder text, overly brief descriptions)."
            )

        # Duplicate warnings
        duplicate_issues = issue_types.get("potential_duplicate", 0)
        if duplicate_issues > 0:
            recommendations.append(
                f"Review {duplicate_issues} potential duplicate programs for possible consolidation."
            )

        # Outlier warnings
        outlier_issues = issue_types.get("statistical_outlier", 0)
        if outlier_issues > 0:
            recommendations.append(
                f"Investigate {outlier_issues} statistical outliers that may indicate data errors."
            )

        # Company consistency issues
        consistency_issues = issue_types.get("company_consistency", 0)
        if consistency_issues > 0:
            recommendations.append(
                f"Review {consistency_issues} inconsistencies among programs from the same organization."
            )

        # Positive reinforcement
        excellent_count = len([r for r in individual_results if r.get("status") == "excellent"])
        good_count = len([r for r in individual_results if r.get("status") == "good"])
        if excellent_count > 0:
            recommendations.append(
                f"Maintain high quality: {excellent_count} programs rated 'excellent'."
            )
        if good_count > 0:
            recommendations.append(
                f"Good foundation: {good_count} programs rated 'good' - consider elevating to 'excellent'."
            )

        # General recommendations if no specific issues
        if not recommendations:
            recommendations.append(
                "Data quality is good. Continue regular validation and consider implementing automated monitoring."
            )

        return recommendations[:10]  # Limit to top 10 recommendations


# Convenience function for external use
def validate_programs(programs: list[dict]) -> dict[str, Any]:
    """
    Validate a list of programs and return quality assessment
    """
    validator = AdvancedDataValidator()
    return validator.validate_program_batch(programs)


if __name__ == "__main__":
    # Example usage and testing
    print("Advanced Data Validator Module")
    print("==============================")

    # Sample program for testing
    sample_program = {
        "id": "test-001",
        "name": "Test Student Ambassador Program",
        "company": "Test Company",
        "apply_url": "https://example.com/apply",
        "status": "Accepting",
        "role_type": "Ambassador",
        "domain": "Tech",
        "eligibility_summary": "Full-time students at accredited universities",
        "location_notes": "Hybrid - remote with optional meetings in New York City",
        "compensation_bucket": "Paid",
        "last_verified": "2024-01-15",
        "short_description": "Represent the company on campus and create engaging content.",
        "responsibilities": [
            "Create weekly social media content",
            "Host monthly events on campus",
            "Engage with student community",
            "Provide feedback on products",
        ],
        "time_commitment": "10-15 hours/week",
        "perks_detail": "Stipend, professional development, networking opportunities",
        "deadlines": {
            "application": "2024-03-01",
            "program_start": "2024-06-01",
            "program_end": "2025-05-31",
        },
        "social_requirements": "Minimum 3 posts per week on Instagram and TikTok using #TestAmbassador",
        "source_url": "https://example.com/program",
        "source_snippet": "Join our ambassador program to represent our brand.",
        "school_restricted": False,
        "notes": "Annual program",
    }

    print("\nTesting validation on sample program...")
    result = validate_programs([sample_program])

    print(f"Overall Score: {result['overall_score']}")
    print(f"Status: {result['status']}")
    print(f"Programs Analyzed: {result['total_programs']}")

    if result["individual_scores"]:
        prog_result = result["individual_scores"][0]
        print(f"\nProgram: {prog_result['program_name']}")
        print(f"Quality Score: {prog_result['quality_score']}")
        print(f"Status: {prog_result['status']}")
        print(f"Completeness: {prog_result['completeness_score']}%")

        if prog_result["issues"]:
            print(f"\nIssues Found ({len(prog_result['issues'])}):")
            for issue in prog_result["issues"][:5]:  # Show first 5 issues
                print(f"  - [{issue['type']}] {issue['message']}")
        else:
            print("\nNo issues found!")

    if result["recommendations"]:
        print("\nRecommendations:")
        for rec in result["recommendations"][:5]:  # Show first 5 recommendations
            print(f"  - {rec}")
