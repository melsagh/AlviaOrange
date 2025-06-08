"""Example hotspot retrieval module."""

from __future__ import annotations

from typing import List


def fetch_hotspots(region: str = "Canada") -> List[str]:
    """Return a list of hotspot identifiers for a given region.

    This is a placeholder implementation that returns sample data.
    """
    sample_data = {
        "Canada": ["AB-001", "BC-123"],
        "USA": ["CA-999", "OR-456"],
    }
    return sample_data.get(region, [])
