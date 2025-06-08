"""Retrieve Canadian air quality data from Environment Canada."""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from typing import Dict

URL = "https://weather.gc.ca/mainmenu/airquality_menu_e.html"


def fetch_air_quality() -> Dict[str, str]:
    """Fetch air quality information from Environment Canada.

    Returns a mapping of city names to their reported air quality index. This
    parser is based on the HTML layout of the Air Quality menu page. If the
    layout changes, this function may need to be updated.
    """
    response = requests.get(URL, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    data: Dict[str, str] = {}

    # Example HTML structure assumption:
    # <table id="AQHI"> <tr><td>City</td><td>Index</td></tr> ...
    for row in soup.select("table tr"):
        cells = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cells) >= 2:
            city, index = cells[0], cells[1]
            data[city] = index
    return data

AQI_SCALE_URL = "https://weather.gc.ca/mainmenu/airquality_health_e.html"
HISTORY_URL_TEMPLATE = (
    "https://dd.weather.gc.ca/air_quality/aqhi/{city}/observation/{date}_aqhi.csv"
)


def _expand_index_range(text: str) -> list[str]:
    """Expand a range like '1-3' into ['1', '2', '3']."""
    text = text.strip()
    if text.endswith("+"):
        return [text]
    if "-" in text:
        start, end = text.split("-", 1)
        return [str(i) for i in range(int(start), int(end) + 1)]
    return [text]


def fetch_aqi_scale() -> Dict[str, Dict[str, str]]:
    """Return mapping of AQHI values to risk bands and messages."""
    response = requests.get(AQI_SCALE_URL, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    mapping: Dict[str, Dict[str, str]] = {}
    for row in soup.select("table tr"):
        cells = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cells) >= 3:
            index_range, band, meaning = cells[0], cells[1], cells[2]
            for val in _expand_index_range(index_range):
                mapping[val] = {"band": band, "meaning": meaning}
    return mapping


def fetch_air_quality_history(city: str, date: str) -> list[dict[str, str]]:
    """Fetch historical AQHI data for a city and date (YYYY-MM-DD)."""
    url = HISTORY_URL_TEMPLATE.format(city=city.lower(), date=date.replace("-", ""))
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    lines = [line for line in response.text.splitlines() if line and not line.startswith("#")]
    if not lines:
        return []

    import csv

    reader = csv.reader(lines)
    header = next(reader, None)
    history = []
    for row in reader:
        if len(row) >= 2:
            history.append({"datetime": row[0], "value": row[1]})
    return history
