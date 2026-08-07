"""Shared HTML parsing helpers for hybrid scrapers."""

from __future__ import annotations

from datetime import date

from bs4 import BeautifulSoup


def today_iso() -> str:
    return date.today().isoformat()


def page_text(soup: BeautifulSoup) -> str:
    return soup.get_text(" ", strip=True)


def first_paragraph(soup: BeautifulSoup, min_length: int = 40) -> str:
    for tag in soup.find_all("p"):
        text = tag.get_text(strip=True)
        if len(text) >= min_length:
            return text
    return ""


def infer_status_from_text(text: str) -> str:
    """Return non-Unknown status only when page text has explicit evidence."""
    lower = text.lower()
    closed_signals = (
        "applications are closed",
        "application period has ended",
        "applications have closed",
        "not accepting applications",
    )
    if any(signal in lower for signal in closed_signals):
        return "Closed"

    accepting_signals = (
        "applications are now open",
        "applications are open",
        "apply now",
        "apply today",
    )
    if any(signal in lower for signal in accepting_signals):
        return "Accepting"

    rolling_signals = (
        "rolling applications",
        "accepting applications on a rolling basis",
        "applications accepted year-round",
    )
    if any(signal in lower for signal in rolling_signals):
        return "Rolling"

    return "Unknown"


def snippet_from_text(text: str, max_length: int = 280) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[: max_length - 3] + "..."
