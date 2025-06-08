"""Minimal HTTP server exposing hotspot retrieval."""

from __future__ import annotations

from fastapi import FastAPI

from .hotspots import fetch_hotspots

app = FastAPI()


@app.get("/hotspots")
def get_hotspots(region: str = "Canada") -> list[str]:
    """Return hotspots for the specified region."""
    return fetch_hotspots(region)
