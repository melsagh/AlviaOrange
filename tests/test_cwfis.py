import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import alviaorange.cwfis as cw
from alviaorange.cwfis import (
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
    BASE_URL,
)


class DummyResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        return None

    def json(self):
        import json
        return json.loads(self.text)


def fake_get_factory(expected_url):
    def fake_get(url, timeout=10):
        assert url == expected_url
        return DummyResponse('{"result": "ok"}')
    return fake_get


def test_fetch_fire_weather_index(monkeypatch):
    url = f"{BASE_URL}/interactive-map/api/fire-weather-index?date=2024-01-01&region=ON"
    monkeypatch.setattr(cw.requests, "get", fake_get_factory(url))
    data = fetch_fire_weather_index("2024-01-01", region="ON")
    assert data["result"] == "ok"


def test_fetch_active_fires(monkeypatch):
    url = f"{BASE_URL}/interactive-map/api/active-fires"
    monkeypatch.setattr(cw.requests, "get", fake_get_factory(url))
    data = fetch_active_fires()
    assert data["result"] == "ok"


def test_fire_danger_wms_tile_url():
    url = fire_danger_wms_tile_url("20230401")
    assert "layers=public:fdr20230401" in url
    assert url.startswith("https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wms?")
    assert "{bbox-epsg-3857}" in url
