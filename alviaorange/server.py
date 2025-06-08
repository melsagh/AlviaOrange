"""Minimal HTTP server exposing hotspot retrieval."""

from __future__ import annotations

from fastapi import FastAPI

from .hotspots import fetch_hotspots
from .air_quality import (
    fetch_air_quality,
    fetch_aqi_scale,
    fetch_air_quality_history,
)
from .cwfis import (
    fetch_fire_weather_index,
    fetch_fire_danger,
    fetch_fire_perimeter,
    fetch_m3_hotspots,
    fetch_season_hotspots,
    fetch_active_fires,
    fetch_forecast_weather_stations,
    fetch_reporting_weather_stations,
    fetch_fire_history,
    fire_danger_wms_tile_url,
)

app = FastAPI()


@app.get("/hotspots")
def get_hotspots(region: str = "Canada") -> list[str] | dict[str, list[str]]:
    """Return hotspots for the specified region or shapefile."""
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


@app.get("/cwfis/fwi")
def get_fire_weather_index(date: str, region: str | None = None) -> dict[str, any]:
    """Return Fire Weather Index for a date."""

    return fetch_fire_weather_index(date, region)


@app.get("/cwfis/fire_danger")
def get_fire_danger(date: str, region: str | None = None) -> dict[str, any]:
    """Return Fire Danger ratings."""

    return fetch_fire_danger(date, region)


@app.get("/cwfis/fire_danger_tile")
def get_fire_danger_tile(date: str) -> str:
    """Return WMS tile URL template for Fire Danger Ratings."""

    return fire_danger_wms_tile_url(date)


@app.get("/cwfis/fire_perimeter")
def get_fire_perimeter(date: str) -> dict[str, any]:
    """Return estimated fire perimeters."""

    return fetch_fire_perimeter(date)


@app.get("/cwfis/m3_hotspots")
def get_m3_hotspots(date: str) -> dict[str, any]:
    """Return M3 hotspot information."""

    return fetch_m3_hotspots(date)


@app.get("/cwfis/season_hotspots")
def get_season_hotspots(year: int) -> dict[str, any]:
    """Return season-to-date hotspots for a year."""

    return fetch_season_hotspots(year)


@app.get("/cwfis/active_fires")
def get_active_fires() -> dict[str, any]:
    """Return currently active fires."""

    return fetch_active_fires()


@app.get("/cwfis/forecast_stations")
def get_forecast_weather_stations() -> dict[str, any]:
    """Return forecast weather station data."""

    return fetch_forecast_weather_stations()


@app.get("/cwfis/reporting_stations")
def get_reporting_weather_stations() -> dict[str, any]:
    """Return reporting weather station data."""

    return fetch_reporting_weather_stations()


@app.get("/cwfis/history")
def get_fire_history(region: str, start: str, end: str) -> dict[str, any]:
    """Return fire history for a region within a date range."""

    return fetch_fire_history(region, start, end)
