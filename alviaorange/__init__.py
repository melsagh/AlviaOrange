"""Core package for AlviaOrange wildfire analytics."""

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
)

__all__ = [
    "fetch_hotspots",
    "fetch_air_quality",
    "fetch_aqi_scale",
    "fetch_air_quality_history",
    "fetch_fire_weather_index",
    "fetch_fire_danger",
    "fetch_fire_perimeter",
    "fetch_m3_hotspots",
    "fetch_season_hotspots",
    "fetch_active_fires",
    "fetch_forecast_weather_stations",
    "fetch_reporting_weather_stations",
    "fetch_fire_history",
]
