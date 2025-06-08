"""Minimal HTTP server exposing hotspot retrieval."""

from __future__ import annotations

from fastapi import FastAPI

from .hotspots import fetch_hotspots
from .air_quality import (
    fetch_air_quality,
    fetch_aqi_scale,
    fetch_air_quality_history,
)

app = FastAPI()


@app.get("/hotspots")
def get_hotspots(region: str = "Canada") -> list[str]:
    """Return hotspots for the specified region."""
    return fetch_hotspots(region)


@app.get("/air_quality")
def get_air_quality() -> dict[str, str]:
    """Return a mapping of city names to air quality index."""
    return fetch_air_quality()


@app.get("/air_quality/scale")
def get_air_quality_scale() -> dict[str, dict[str, str]]:
    """Return the AQHI scale mapping."""
    return fetch_aqi_scale()


@app.get("/air_quality/history")
def get_air_quality_history(
    city: str, start: str, end: str | None = None
) -> list[dict[str, str]]:
    """Return historical AQHI data for a city within a date range."""
    return fetch_air_quality_history(city, start, end)
