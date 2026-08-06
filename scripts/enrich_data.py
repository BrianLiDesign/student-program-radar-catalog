"""
Data enrichment system for student programs
Adds derived fields to enhance program data for analysis and display
"""

import json
import re
from datetime import datetime
from typing import Optional


def enrich_program_data(program: dict) -> dict:
    """
    Enrich a single program record with derived fields
    Returns a new dictionary with original data plus enrichments
    """
    # Create a copy to avoid modifying the original
    enriched = program.copy()

    # Add metadata about enrichment
    enriched["_enrichment"] = {"timestamp": datetime.now().isoformat(), "version": "1.0"}

    # 1. Program duration calculation from deadlines
    enriched = _add_program_duration(enriched)

    # 2. Application complexity score based on requirements
    enriched = _add_application_complexity_score(enriched)

    # 3. Geo-tagging for location-based programs
    enriched = _add_geotagging(enriched)

    # 4. Competitive analysis fields (comparing similar programs)
    # Note: This would require comparing against other programs,
    # so we'll add placeholders that would be filled in batch processing

    # 5. Additional derived fields
    enriched = _add_temporal_features(enriched)
    enriched = _add_engagement_indicators(enriched)

    return enriched


def _add_program_duration(program: dict) -> dict:
    """Calculate program duration from deadlines"""
    if "deadlines" not in program or not isinstance(program["deadlines"], dict):
        return program

    deadlines = program["deadlines"]
    start_date_str = deadlines.get("program_start")
    end_date_str = deadlines.get("program_end")

    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

            if end_date > start_date:
                delta = end_date - start_date
                days = delta.days

                # Add duration in different formats
                program["program_duration_days"] = days
                program["program_duration_weeks"] = round(days / 7, 1)
                program["program_duration_months"] = round(days / 30.44, 1)  # Average month length

                # Human-readable format
                if days >= 365:
                    years = days // 365
                    remaining_days = days % 365
                    if remaining_days >= 30:
                        months = remaining_days // 30
                        program["program_duration_human"] = (
                            f"{years} year{'s' if years > 1 else ''}, {months} month{'s' if months > 1 else ''}"
                        )
                    else:
                        program["program_duration_human"] = (
                            f"{years} year{'s' if years > 1 else ''}"
                        )
                elif days >= 30:
                    months = days // 30
                    remaining_days = days % 30
                    if remaining_days >= 7:
                        weeks = remaining_days // 7
                        program["program_duration_human"] = (
                            f"{months} month{'s' if months > 1 else ''}, {weeks} week{'s' if weeks > 1 else ''}"
                        )
                    else:
                        program["program_duration_human"] = (
                            f"{months} month{'s' if months > 1 else ''}"
                        )
                elif days >= 7:
                    weeks = days // 7
                    program["program_duration_human"] = f"{weeks} week{'s' if weeks > 1 else ''}"
                else:
                    program["program_duration_human"] = f"{days} day{'s' if days > 1 else ''}"

        except ValueError:
            # If date parsing fails, skip duration calculation
            pass

    return program


def _add_application_complexity_score(program: dict) -> dict:
    """
    Calculate an application complexity score (0-100) based on:
    - Number of responsibilities
    - Time commitment
    - Special requirements (social media, etc.)
    - Application process complexity (inferred from deadlines, etc.)
    """
    score = 0
    max_score = 100

    # Factor 1: Responsibilities count (0-25 points)
    responsibilities = program.get("responsibilities", [])
    if isinstance(responsibilities, list):
        resp_count = len(responsibilities)
        if resp_count >= 10:
            score += 25
        elif resp_count >= 6:
            score += 20
        elif resp_count >= 3:
            score += 15
        elif resp_count >= 1:
            score += 10

    # Factor 2: Time commitment (0-20 points)
    time_commitment = program.get("time_commitment", "").lower()
    hours_per_week = _extract_hours_per_week(time_commitment)
    if hours_per_week is not None:
        if hours_per_week >= 20:
            score += 20
        elif hours_per_week >= 15:
            score += 15
        elif hours_per_week >= 10:
            score += 10
        elif hours_per_week >= 5:
            score += 5

    # Factor 3: Social/media requirements (0-15 points)
    social_req = program.get("social_requirements", "")
    if social_req and isinstance(social_req, str):
        social_req_lower = social_req.lower()
        # Look for indicators of significant social media requirements
        social_indicators = [
            "post",
            "share",
            "content",
            "follower",
            "engagement",
            "social media",
            "twitter",
            "instagram",
            "linkedin",
            "blog",
            "video",
        ]
        matches = sum(1 for indicator in social_indicators if indicator in social_req_lower)
        if matches >= 3:
            score += 15
        elif matches >= 2:
            score += 10
        elif matches >= 1:
            score += 5

        # Check for frequency requirements
        freq_patterns = [r"\d+\s*[xX]", r"\d+\s*times?", r"daily", r"weekly", r"monthly"]
        for pattern in freq_patterns:
            if re.search(pattern, social_req_lower):
                score += 5
                break

    # Factor 4: Application process complexity (0-20 points)
    # Look for multiple deadlines, complex application requirements
    deadlines = program.get("deadlines", {})
    if isinstance(deadlines, dict):
        deadline_count = len(
            [
                k
                for k in deadlines.keys()
                if k not in ["application", "program_start", "program_end"]
            ]
        )
        if deadline_count >= 3:
            score += 20
        elif deadline_count >= 2:
            score += 15
        elif deadline_count >= 1:
            score += 10

    # Check for multiple application rounds
    if isinstance(deadlines, dict):
        if any("round" in str(k).lower() for k in deadlines.keys()):
            score += 10

    # Factor 5: Prestige/selectivity indicators (0-20 points)
    # Look for competitive indicators in description
    text_fields = [
        program.get("short_description", ""),
        program.get("eligibility_summary", ""),
        " ".join(program.get("responsibilities", []))
        if isinstance(program.get("responsibilities"), list)
        else "",
    ]
    combined_text = " ".join(text_fields).lower()

    competitive_indicators = [
        "competitive",
        "selective",
        "prestigious",
        "elite",
        "top-tier",
        "rigorous",
        "intensive",
        "rigorous selection",
        "limited spots",
        "application required",
        "interview",
        "selection process",
    ]

    matches = sum(1 for indicator in competitive_indicators if indicator in combined_text)
    if matches >= 4:
        score += 20
    elif matches >= 3:
        score += 15
    elif matches >= 2:
        score += 10
    elif matches >= 1:
        score += 5

    # Normalize score to 0-100 range
    final_score = min(max_score, max(0, score))
    program["application_complexity_score"] = round(float(final_score), 1)

    # Add category
    if final_score >= 80:
        program["application_complexity_level"] = "Very High"
    elif final_score >= 60:
        program["application_complexity_level"] = "High"
    elif final_score >= 40:
        program["application_complexity_level"] = "Medium"
    elif final_score >= 20:
        program["application_complexity_level"] = "Low"
    else:
        program["application_complexity_level"] = "Very Low"

    return program


def _extract_hours_per_week(time_str: str) -> Optional[float]:
    """Extract hours per week from time commitment string"""
    if not isinstance(time_str, str):
        return None

    # Look for patterns like "10 hours/week", "5-15 hrs/wk", etc.
    patterns = [
        r"(\d+(?:(\d+(?:\.\d+)?)\s*[-－]\s*(\d+(?:\.\d+)?))\s*(?:hours?|hrs?)\s*(?:/|per)?\s*week",
        r"(?:(\d+(?:\.\d+)?)\s*(?:hours?|hrs?))\s*(?:/|per)?\s*week",
        r"(?:(\d+(?:\.\d+)?)\s*[-－]\s*(\d+(?:\.\d+)?))\s*(?:hours?|hrs?)",
        r"(?:(\d+(?:\.\d+)?)\s*(?:hours?|hrs?))",
    ]

    for pattern in patterns:
        match = re.search(pattern, re.IGNORECASE)
        if match:
            try:
                if len(match.groups()) >= 2 and match.group(1) and match.group(2):
                    # Range like "5-15 hours/week"
                    low = float(match.group(1))
                    high = float(match.group(2))
                    return (low + high) / 2  # Return average
                elif len(match.groups()) >= 1 and match.group(1):
                    # Single value like "10 hours/week" or just "10 hours"
                    return float(match.group(1))
            except ValueError:
                continue

    return None


def _add_geotagging(program: dict) -> dict:
    """Add geographical information based on location notes"""
    location_notes = program.get("location_notes", "")
    if not isinstance(location_notes, str):
        return program

    location_lower = location_notes.lower()

    # Initialize geotagging fields
    program["is_remote"] = False
    program["is_hybrid"] = False
    program["is_location_specific"] = False
    program["detected_regions"] = []
    program["detected_countries"] = []
    program["detected_cities"] = []

    # Check for remote indicators
    remote_indicators = ["remote", "virtual", "online", "distributed", "anywhere", "telecommute"]
    if any(indicator in location_lower for indicator in remote_indicators):
        program["is_remote"] = True

    # Check for hybrid indicators
    hybrid_indicators = ["hybrid", "mixed", "partially remote", "flexible"]
    if any(indicator in location_lower for indicator in hybrid_indicators):
        program["is_hybrid"] = True

    # If not remote or hybrid, likely location-specific
    if not program["is_remote"] and not program["is_hybrid"] and location_notes.strip():
        program["is_location_specific"] = True

    # Simple region/country detection (could be enhanced with a proper geocoding service)
    us_indicators = ["united states", "usa", "us ", ", us", "united states of america", "america"]
    eu_indicators = [
        "europe",
        "european union",
        "eu ",
        "uk",
        "united kingdom",
        "france",
        "germany",
        "spain",
        "italy",
        "netherlands",
        "sweden",
        "canada",
        "australia",
    ]
    asia_indicators = ["asia", "asia-pacific", "jap", "china", "india", "singapore", "korea"]

    # Check for country/region mentions
    if any(indicator in location_lower for indicator in us_indicators):
        program["detected_countries"].append("United States")
        program["detected_regions"].append("North America")

    if any(indicator in location_lower for indicator in eu_indicators):
        if "uk" in location_lower or "united kingdom" in location_lower:
            program["detected_countries"].append("United Kingdom")
        # Add other EU countries as detected
        program["detected_regions"].append("Europe")

    if any(indicator in location_lower for indicator in asia_indicators):
        program["detected_regions"].append("Asia-Pacific")

    # US states for more detailed detection
    us_states = [
        "alabama",
        "alaska",
        "arizona",
        "arkansas",
        "california",
        "colorado",
        "connecticut",
        "delaware",
        "florida",
        "georgia",
        "hawaii",
        "idaho",
        "illinois",
        "indiana",
        "iowa",
        "kansas",
        "kentucky",
        "louisiana",
        "maine",
        "maryland",
        "massachusetts",
        "michigan",
        "minnesota",
        "mississippi",
        "missouri",
        "montana",
        "nebraska",
        "nevada",
        "new hampshire",
        "new jersey",
        "new mexico",
        "new york",
        "north carolina",
        "north dakota",
        "ohio",
        "oklahoma",
        "oregon",
        "pennsylvania",
        "rhode island",
        "south carolina",
        "south dakota",
        "tennessee",
        "texas",
        "utah",
        "vermont",
        "virginia",
        "washington",
        "west virginia",
        "wisconsin",
        "wyoming",
        "district of columbia",
        "dc",
    ]

    for state in us_states:
        if state in location_lower:
            program["detected_cities"].append(
                state.title()
            )  # Simplified - would be better with actual city detection
            if "United States" not in program["detected_countries"]:
                program["detected_countries"].append("United States")
            if "North America" not in program["detected_regions"]:
                program["detected_regions"].append("North America")
            break  # Just add one for simplicity

    # Major tech hubs detection
    tech_hubs = {
        "silicon valley": ["san francisco", "san jose", "palo alto", "mountain view"],
        "seattle": ["seattle", "bellevue", "redmond"],
        "new york": ["new york", "nyc", "manhattan", "brooklyn"],
        "boston": ["boston", "cambridge"],
        "los angeles": ["los angeles", "la ", "santa monica"],
        "austin": ["austin"],
        "chicago": ["chicago"],
        "atlanta": ["atlanta"],
    }

    for region, cities in tech_hubs.items():
        if region in location_lower:
            program["detected_regions"].append(region.title())
            for city in cities:
                if city in location_lower:
                    program["detected_cities"].append(city.title())

    # Remove duplicates
    program["detected_regions"] = list(set(program["detected_regions"]))
    program["detected_countries"] = list(set(program["detected_countries"]))
    program["detected_cities"] = list(set(program["detected_cities"]))

    return program


def _add_temporal_features(program: dict) -> dict:
    """Add time-based features"""
    now = datetime.now()

    # Days since last verified
    last_verified_str = program.get("last_verified")
    if last_verified_str:
        try:
            last_verified = datetime.strptime(last_verified_str, "%Y-%m-%d")
            days_since_verified = (now - last_verified).days
            program["days_since_last_verified"] = days_since_verified

            # Freshness score (0-100, where 100 is very fresh)
            if days_since_verified <= 30:
                freshness_score = 100
            elif days_since_verified <= 90:
                # Linear decay from 100 to 70 over 90 days
                freshness_score = 100 - (days_since_verified - 30) * 30 / 60
            elif days_since_verified <= 365:
                # Linear decay from 70 to 30 over 275 days
                freshness_score = 70 - (days_since_verified - 90) * 40 / 275
            else:
                # Below 30 for very old data
                freshness_score = max(0, 30 - (days_since_verified - 365) * 20 / 365)

            program["data_freshness_score"] = round(max(0, min(100, freshness_score)), 1)
        except ValueError:
            pass

    # Days until application deadline (if available)
    deadlines = program.get("deadlines", {})
    if isinstance(deadlines, dict):
        app_deadline_str = deadlines.get("application")
        if app_deadline_str:
            try:
                app_deadline = datetime.strptime(app_deadline_str, "%Y-%m-%d")
                days_until_deadline = (app_deadline - now).days
                program["days_until_application_deadline"] = max(
                    0, days_until_deadline
                )  # Don't show negative

                # Urgency score (0-100, where 100 is very urgent/deadline soon)
                if days_until_deadline < 0:
                    urgency_score = 0  # Already past
                elif days_until_deadline == 0:
                    urgency_score = 100  # Due today
                elif days_until_deadline <= 7:
                    urgency_score = 100  # Due within a week
                elif days_until_deadline <= 30:
                    # Scale from 100 down to 50 over 30 days
                    urgency_score = 100 - (days_until_deadline - 7) * 50 / 23
                elif days_until_deadline <= 90:
                    # Scale from 50 down to 20 over 60 days
                    urgency_score = 50 - (days_until_deadline - 30) * 30 / 60
                else:
                    urgency_score = max(0, 20 - (days_until_deadline - 90) * 20 / 275)

                application_deadline_urgency = round(max(0, min(100, urgency_score)), 1)
                program["application_deadline_urgency_score"] = application_deadline_urgency
            except ValueError:
                pass

    return program


def _add_engagement_indicators(program: dict) -> dict:
    """Add indicators about potential engagement/viral coefficient"""
    score = 0

    # Social media readiness
    social_req = program.get("social_requirements", "")
    if isinstance(social_req, str) and social_req.strip():
        # Points for having social requirements
        score += 20

        # Bonus for specific platforms mentioned
        social_lower = social_req.lower()
        if "instagram" in social_lower or "twitter" in social_lower or "tiktok" in social_lower:
            score += 15
        elif "linkedin" in social_lower or "youtube" in social_lower:
            score += 10
        elif "facebook" in social_lower or "blog" in social_lower:
            score += 5

    # Content creation expectations
    responsibilities = program.get("responsibilities", [])
    if isinstance(responsibilities, list):
        content_keywords = [
            "create",
            "content",
            "design",
            "video",
            "photo",
            "blog",
            "post",
            "social",
        ]
        content_count = sum(
            1
            for resp in responsibilities
            if isinstance(resp, str)
            and any(keyword in resp.lower() for keyword in content_keywords)
        )
        if content_count >= 3:
            score += 20
        elif content_count >= 2:
            score += 15
        elif content_count >= 1:
            score += 10

    # Community engagement
    community_keywords = ["community", "engage", "outreach", "event", "workshop", "mentor", "teach"]
    resp_text = " ".join(responsibilities) if isinstance(responsibilities, list) else ""
    desc_text = program.get("short_description", "") + " " + program.get("eligibility_summary", "")
    combined_text = (resp_text + " " + desc_text).lower()

    community_matches = sum(1 for keyword in community_keywords if keyword in combined_text)
    if community_matches >= 3:
        score += 20
    elif community_matches >= 2:
        score += 15
    elif community_matches >= 1:
        score += 10

    # Innovation/creativity indicators
    innovation_keywords = [
        "innovate",
        "innovation",
        "creative",
        "creativity",
        "design",
        "build",
        "develop",
        "launch",
    ]
    innovation_matches = sum(1 for keyword in innovation_keywords if keyword in combined_text)
    if innovation_matches >= 3:
        score += 15
    elif innovation_matches >= 2:
        score += 10
    elif innovation_matches >= 1:
        score += 5

    # Normalize to 0-100
    engagement_score = min(100, max(0, score))
    program["engagement_potential_score"] = round(float(engagement_score), 1)

    # Add engagement level category
    if engagement_score >= 80:
        program["engagement_level"] = "Very High"
    elif engagement_score >= 60:
        program["engagement_level"] = "High"
    elif engagement_score >= 40:
        program["engagement_level"] = "Medium"
    elif engagement_score >= 20:
        program["engagement_level"] = "Low"
    else:
        program["engagement_level"] = "Very Low"

    return program


def batch_enrich_programs(programs: list[dict]) -> list[dict]:
    """
    Enrich a batch of programs and add comparative analysis
    """
    enriched_programs = []

    # First pass: individual enrichment
    for program in programs:
        enriched = enrich_program_data(program)
        enriched_programs.append(enriched)

    # Second pass: add comparative features (would need more sophisticated implementation)
    # For now, we'll add placeholder fields that could be computed in a more advanced version

    return enriched_programs


def add_derived_fields_schema(schema: dict) -> dict:
    """
    Add definitions for derived fields to the JSON schema
    Returns updated schema
    """
    # Make a copy to avoid modifying original
    updated_schema = json.loads(json.dumps(schema))

    # Define properties for derived fields
    derived_properties = {
        "program_duration_days": {
            "type": "integer",
            "minimum": 0,
            "description": "Program duration in days calculated from start/end dates",
        },
        "program_duration_weeks": {
            "type": "number",
            "minimum": 0,
            "description": "Program duration in weeks",
        },
        "program_duration_months": {
            "type": "number",
            "minimum": 0,
            "description": "Program duration in months",
        },
        "program_duration_human": {
            "type": "string",
            "description": "Human-readable program duration",
        },
        "application_complexity_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Calculated application complexity score (0-100)",
        },
        "application_complexity_level": {
            "type": "string",
            "enum": ["Very Low", "Low", "Medium", "High", "Very High"],
            "description": "Categorical application complexity level",
        },
        "is_remote": {"type": "boolean", "description": "Whether the program is remote/virtual"},
        "is_hybrid": {"type": "boolean", "description": "Whether the program is hybrid format"},
        "is_location_specific": {
            "type": "boolean",
            "description": "Whether the program is location-specific",
        },
        "detected_regions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Detected geographical regions",
        },
        "detected_countries": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Detected countries",
        },
        "detected_cities": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Detected cities",
        },
        "days_since_last_verified": {
            "type": "integer",
            "minimum": 0,
            "description": "Days since the program information was last verified",
        },
        "data_freshness_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Score indicating how fresh the data is (0-100)",
        },
        "days_until_application_deadline": {
            "type": "integer",
            "minimum": 0,
            "description": "Days until application deadline",
        },
        "application_deadline_urgency_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Urgency score based on proximity to application deadline",
        },
        "engagement_potential_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Score indicating potential for engagement/viral spread",
        },
        "engagement_level": {
            "type": "string",
            "enum": ["Very Low", "Low", "Medium", "High", "Very High"],
            "description": "Categorical engagement level",
        },
    }

    # Add properties to schema
    if "properties" not in updated_schema:
        updated_schema["properties"] = {}

    updated_schema["properties"].update(derived_properties)

    # Note: We don't add these to "required" since they are derived/computed fields

    return updated_schema


if __name__ == "__main__":
    # Example usage and testing
    import json

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

    print("Testing enrichment on sample program...")
    enriched = enrich_program_data(sample_program)

    print("\nOriginal program keys:", list(sample_program.keys()))
    print("Enriched program keys:", list(enriched.keys()))

    # Show some of the added fields
    added_fields = [k for k in enriched.keys() if k not in sample_program.keys()]
    print(f"\nAdded {len(added_fields)} derived fields:")
    for field in sorted(added_fields):
        if not field.startswith("_"):  # Skip internal metadata
            print(f"  {field}: {enriched[field]}")

    # Example of batch enrichment
    print("\n--- Batch Enrichment Example ---")
    batch_result = batch_enrich_programs([sample_program])
    print(f"Processed {len(batch_result)} programs")
