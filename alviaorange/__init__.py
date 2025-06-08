"""Core package for AlviaOrange wildfire analytics."""

from .hotspots import fetch_hotspots
from .air_quality import (
    fetch_air_quality,
    fetch_aqi_scale,
    fetch_air_quality_history,
)

__all__ = [
    "fetch_hotspots",
    "fetch_air_quality",
    "fetch_aqi_scale",
    "fetch_air_quality_history",
]
