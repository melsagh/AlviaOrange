import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from alviaorange.air_quality import (
    fetch_air_quality,
    fetch_aqi_scale,
    fetch_air_quality_history,
    URL,
    AQI_SCALE_URL,
    HISTORY_URL_TEMPLATE,
)


class DummyResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self) -> None:  # noqa: D401 - simple no-op
        """Mimic requests' Response.raise_for_status."""
        return None


def test_fetch_air_quality(monkeypatch):
    html = """
    <html><body>
    <table id='aqhi'>
        <tr><td>Toronto</td><td>5</td></tr>
        <tr><td>Vancouver</td><td>3</td></tr>
    </table>
    </body></html>
    """

    def fake_get(url, timeout=10):
        assert url == URL
        return DummyResponse(html)

    import alviaorange.air_quality as aq

    monkeypatch.setattr(aq.requests, "get", fake_get)

    data = fetch_air_quality()
    assert data == {"Toronto": "5", "Vancouver": "3"}


def test_fetch_aqi_scale(monkeypatch):
    html = """
    <table>
        <tr><td>1-3</td><td>Low</td><td>Good</td></tr>
        <tr><td>4-6</td><td>Moderate</td><td>Caution</td></tr>
        <tr><td>7-9</td><td>High</td><td>Limit activities</td></tr>
        <tr><td>10+</td><td>Very High</td><td>Avoid outdoors</td></tr>
    </table>
    """

    def fake_get(url, timeout=10):
        assert url == AQI_SCALE_URL
        return DummyResponse(html)

    import alviaorange.air_quality as aq

    monkeypatch.setattr(aq.requests, "get", fake_get)

    data = fetch_aqi_scale()
    assert data["1"]["band"] == "Low"
    assert data["5"]["band"] == "Moderate"
    assert data["10+"]["band"] == "Very High"


def test_fetch_air_quality_history(monkeypatch):
    csv = """Date,Value\n2024-01-01T00:00Z,3\n2024-01-01T01:00Z,4\n"""

    def fake_get(url, timeout=10):
        assert "toronto" in url
        assert "2024010" in url  # allows 20240101 or 20240102
        return DummyResponse(csv)

    import alviaorange.air_quality as aq

    monkeypatch.setattr(aq.requests, "get", fake_get)

    data = fetch_air_quality_history("Toronto", "2024-01-01", "2024-01-02")
    assert data[0]["value"] == "3"
    assert data[1]["datetime"].endswith("01:00Z")


def test_history_invalid_range(monkeypatch):
    import alviaorange.air_quality as aq

    csv = "Date,Value\n"

    def fake_get(url, timeout=10):
        return DummyResponse(csv)

    monkeypatch.setattr(aq.requests, "get", fake_get)

    with pytest.raises(ValueError):
        fetch_air_quality_history("Toronto", "2024-01-02", "2024-01-01")
