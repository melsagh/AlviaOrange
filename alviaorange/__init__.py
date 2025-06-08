"""Core package for AlviaOrange wildfire analytics.

The top level package lazily exposes helpers from the various submodules so that
optional heavy dependencies are only imported when the corresponding function is
first accessed.  This avoids ``ImportError`` issues for users that only need a
subset of the functionality.
"""

from importlib import import_module

_AIR_QUALITY_FUNCS = {
    "fetch_air_quality",
    "fetch_aqi_scale",
    "fetch_air_quality_history",
}

_CWFIS_FUNCS = {
    "fetch_fire_weather_index",
    "fetch_fire_danger",
    "fetch_fire_perimeter",
    "fetch_m3_hotspots",
    "fetch_season_hotspots",
    "fetch_active_fires",
    "fetch_forecast_weather_stations",
    "fetch_reporting_weather_stations",
    "fetch_fire_history",
    "fire_danger_wms_tile_url",
}

_HOTSPOT_FUNCS = {"fetch_hotspots"}

__all__ = sorted(_AIR_QUALITY_FUNCS | _CWFIS_FUNCS | _HOTSPOT_FUNCS)


def __getattr__(name: str):
    """Dynamically import and return the requested helper."""

    if name in _HOTSPOT_FUNCS:
        module = import_module(".hotspots", __name__)
        return getattr(module, name)
    if name in _AIR_QUALITY_FUNCS:
        module = import_module(".air_quality", __name__)
        return getattr(module, name)
    if name in _CWFIS_FUNCS:
        module = import_module(".cwfis", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
