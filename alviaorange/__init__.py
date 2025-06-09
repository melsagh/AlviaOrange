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
    "fire_weather_index_wms_tile_url",
    "fire_perimeter_wms_tile_url",
    "m3_hotspots_wms_tile_url",
    "season_hotspots_wms_tile_url",
    "active_fires_wms_tile_url",
    "forecast_weather_stations_wms_tile_url",
    "reporting_weather_stations_wms_tile_url",
    "fire_history_wms_tile_url",
}

_HOTSPOT_FUNCS = {"fetch_hotspots"}

_WEATHER_STATION_FUNCS = {
    "fetch_climate_stations",
    "find_nearest_stations", 
    "get_station_weather_data",
    "get_multi_station_data",
    "weather_station_workflow",
}

__all__ = sorted(_AIR_QUALITY_FUNCS | _CWFIS_FUNCS | _HOTSPOT_FUNCS | _WEATHER_STATION_FUNCS)


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
    if name in _WEATHER_STATION_FUNCS:
        module = import_module(".weather_stations", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
