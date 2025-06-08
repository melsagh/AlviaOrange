"""Client for accessing CWFIS interactive map layers."""

from __future__ import annotations

import requests
from typing import Any, Dict

BASE_URL = "https://cwfis.cfs.nrcan.gc.ca"  # Default API base


def fetch_layer(layer: str, **params: str) -> Dict[str, Any]:
    """Return JSON for a given interactive map layer.

    Parameters
    ----------
    layer:
        Name of the desired layer, e.g. ``"fire-weather-index"``.
    **params:
        Additional query parameters such as ``date`` or ``region``.
    """

    query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
    url = f"{BASE_URL}/interactive-map/api/{layer}"
    if query:
        url = f"{url}?{query}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


# Convenience wrappers for common layers

def fetch_fire_weather_index(date: str, region: str | None = None) -> Dict[str, Any]:
    """Fetch Fire Weather Index values for a specific date."""

    return fetch_layer("fire-weather-index", date=date, region=region)


def fetch_fire_danger(date: str, region: str | None = None) -> Dict[str, Any]:
    """Fetch Fire Danger ratings for a specific date."""

    return fetch_layer("fire-danger", date=date, region=region)


def fetch_fire_perimeter(date: str) -> Dict[str, Any]:
    """Fetch Fire Perimeter estimate for a given date."""

    return fetch_layer("fire-perimeter", date=date)


def fetch_m3_hotspots(date: str) -> Dict[str, Any]:
    """Fetch M3 Hotspot data for a date."""

    return fetch_layer("m3-hotspots", date=date)


def fetch_season_hotspots(year: int) -> Dict[str, Any]:
    """Fetch season-to-date hotspots for a year."""

    return fetch_layer("season-hotspots", year=str(year))


def fetch_active_fires() -> Dict[str, Any]:
    """Fetch data for currently active fires."""

    return fetch_layer("active-fires")


def fetch_forecast_weather_stations() -> Dict[str, Any]:
    """Fetch forecast weather station information."""

    return fetch_layer("forecast-weather-stations")


def fetch_reporting_weather_stations() -> Dict[str, Any]:
    """Fetch reporting weather station information."""

    return fetch_layer("reporting-weather-stations")


def fetch_fire_history(region: str, start: str, end: str) -> Dict[str, Any]:
    """Fetch fire history records for a region within a date range."""

    return fetch_layer("fire-history", region=region, start=start, end=end)


def fire_danger_wms_tile_url(date: str | int) -> str:
    """Return WMS tile URL template for Fire Danger Ratings.

    Parameters
    ----------
    date:
        Date in ``YYYYMMDD`` format used by the WMS layer names.
    """

    date_str = str(date)
    return (
        "https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wms?"
        "service=WMS&version=1.1.1&request=GetMap&"
        f"layers=public:fdr{date_str}&"
        "styles=cffdrs_fdr_opaque&"
        "format=image/png&transparent=true&"
        "srs=EPSG:3857&bbox={bbox-epsg-3857}&"
        "width=256&height=256"
    )
