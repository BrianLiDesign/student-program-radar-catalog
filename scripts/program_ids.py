"""Canonical program ID generation for the catalog."""

from __future__ import annotations

import uuid

# Stable namespace for all catalog program IDs.
CATALOG_NAMESPACE = uuid.UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")


def generate_program_id(company: str, name: str) -> str:
    """
    Generate a deterministic UUID v5 for a program.

    The key is normalized ``company|name`` so the same program always receives
    the same ID across scraper runs.
    """
    company_key = company.strip().lower()
    name_key = name.strip().lower()
    return str(uuid.uuid5(CATALOG_NAMESPACE, f"{company_key}|{name_key}"))
