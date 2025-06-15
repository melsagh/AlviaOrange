"""
Hotspot detection and management module for wildfire monitoring.

This module provides functions to detect and retrieve fire hotspots from various
satellite sources including NASA FIRMS, VIIRS, and MODIS data.
"""

from __future__ import annotations

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from uuid import uuid4

from pathlib import Path

import shapefile  # type: ignore
from shapely.geometry import Polygon, shape
from shapely.ops import unary_union, transform
from pyproj import CRS, Transformer

from .schemas import (
    Hotspot, HotspotQueryResult, HotspotSource, HotspotMetadata,
    ZoneBounds, Coordinates, TimeRange, APIResponse, ErrorResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# Simplistic polygon definitions for Canada and the USA. These are rough
# bounding boxes purely for demonstration purposes.
_CANADA_POLYGON = Polygon([(-141, 41), (-52, 41), (-52, 83), (-141, 83)])
_USA_POLYGON = Polygon([(-125, 24), (-66, 24), (-66, 49), (-125, 49)])

# Mapping of region name to polygon
REGION_SHAPES: Dict[str, Polygon] = {
    "Canada": _CANADA_POLYGON,
    "USA": _USA_POLYGON,
}

# API Configuration
FIRMS_BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
VIIRS_BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"

# Default API key - should be set via environment variable in production
DEFAULT_API_KEY = "your_nasa_firms_api_key_here"

class HotspotDetectionError(Exception):
    """Custom exception for hotspot detection errors."""
    pass

class APIConnectionError(Exception):
    """Custom exception for API connection issues."""
    pass

def _read_shapefile(path: Path) -> Polygon:
    """Return the union of all geometries in a shapefile in WGS84 coordinates."""

    reader = shapefile.Reader(str(path))
    geometries = [shape(s.__geo_interface__) for s in reader.shapes()]
    geom = unary_union(geometries)

    prj_file = path.with_suffix(".prj")
    if prj_file.exists():
        prj_txt = prj_file.read_text().strip()
        if prj_txt:
            try:
                src_crs = CRS.from_wkt(prj_txt)
            except Exception:
                try:
                    src_crs = CRS.from_user_input(prj_txt)
                except Exception:
                    src_crs = None
            if src_crs and src_crs != CRS.from_epsg(4326):
                transformer = Transformer.from_crs(src_crs, 4326, always_xy=True)
                geom = transform(transformer.transform, geom)

    return geom

def _fetch_by_region_name(name: str) -> List[str]:
    """Internal helper returning hotspot list for a named region."""

    sample_data = {
        "Canada": ["AB-001", "BC-123"],
        "USA": ["CA-999", "OR-456"],
    }
    return sample_data.get(name, [])

def fetch_hotspots(
    region: Union[str, Path] = "Canada",
) -> Union[List[str], Dict[str, List[str]]]:
    """Return hotspot identifiers for a region or regions defined by a shapefile."""

    path = Path(region)
    if path.exists() and path.suffix.lower() == ".shp":
        geom = _read_shapefile(path)
        results: Dict[str, List[str]] = {}
        for name, poly in REGION_SHAPES.items():
            if poly.intersects(geom):
                results[name] = _fetch_by_region_name(name)
        return results

    return _fetch_by_region_name(str(region))

def detect_hotspots_for_zone(
    zone_bounds: Dict[str, float],
    time_range: Dict[str, str],
    sources: List[str] = ["VIIRS", "MODIS", "FIRMS"],
    min_confidence: int = 70,
    api_key: Optional[str] = None
) -> Dict:
    """
    Detect active fire hotspots within a geographical zone.
    
    Args:
        zone_bounds: Dictionary with keys 'north', 'south', 'east', 'west'
        time_range: Dictionary with keys 'start_date', 'end_date' (ISO format strings)
        sources: List of data sources to query
        min_confidence: Minimum confidence threshold (0-100)
        api_key: NASA FIRMS API key
        
    Returns:
        Dictionary containing hotspots list, total count, and query time
        
    Raises:
        HotspotDetectionError: When detection fails
        APIConnectionError: When API connection fails
        ValueError: When input parameters are invalid
    """
    try:
        # Validate inputs
        bounds = ZoneBounds(**zone_bounds)
        time_range_obj = TimeRange(
            start_date=datetime.fromisoformat(time_range['start_date'].replace('Z', '+00:00')),
            end_date=datetime.fromisoformat(time_range['end_date'].replace('Z', '+00:00'))
        )
        
        # Use provided API key or default
        key = api_key or DEFAULT_API_KEY
        
        all_hotspots = []
        
        for source in sources:
            try:
                hotspots = _fetch_hotspots_from_source(
                    bounds, time_range_obj, source, min_confidence, key
                )
                all_hotspots.extend(hotspots)
            except Exception as e:
                logger.warning(f"Failed to fetch from {source}: {str(e)}")
                continue
        
        # Remove duplicates based on coordinates and timestamp
        unique_hotspots = _remove_duplicate_hotspots(all_hotspots)
        
        # Filter by confidence
        filtered_hotspots = [
            h for h in unique_hotspots 
            if h.confidence is None or h.confidence >= min_confidence
        ]
        
        result = HotspotQueryResult(
            hotspots=filtered_hotspots,
            total_count=len(filtered_hotspots),
            query_time=datetime.now()
        )
        
        return result.dict()
        
    except Exception as e:
        logger.error(f"Hotspot detection failed: {str(e)}")
        raise HotspotDetectionError(f"Failed to detect hotspots: {str(e)}")

def get_active_hotspots(
    zone_bounds: Dict[str, float],
    hours_back: int = 24,
    min_confidence: int = 70,
    api_key: Optional[str] = None
) -> Dict:
    """
    Get currently active hotspots (within specified hours).
    
    Args:
        zone_bounds: Dictionary with keys 'north', 'south', 'east', 'west'
        hours_back: Number of hours to look back for active hotspots
        min_confidence: Minimum confidence threshold
        api_key: NASA FIRMS API key
        
    Returns:
        Dictionary containing active hotspots
        
    Raises:
        HotspotDetectionError: When detection fails
    """
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        time_range = {
            'start_date': start_time.isoformat() + 'Z',
            'end_date': end_time.isoformat() + 'Z'
        }
        
        return detect_hotspots_for_zone(
            zone_bounds=zone_bounds,
            time_range=time_range,
            sources=["VIIRS", "MODIS"],  # Use most recent data sources
            min_confidence=min_confidence,
            api_key=api_key
        )
        
    except Exception as e:
        logger.error(f"Active hotspot retrieval failed: {str(e)}")
        raise HotspotDetectionError(f"Failed to get active hotspots: {str(e)}")

def get_hotspots_near_point(
    lat: float,
    lng: float,
    radius_km: float,
    limit: int = 100,
    hours_back: int = 24,
    api_key: Optional[str] = None
) -> Dict:
    """
    Find hotspots within radius of specific coordinates.
    
    Args:
        lat: Latitude of center point
        lng: Longitude of center point
        radius_km: Search radius in kilometers
        limit: Maximum number of hotspots to return
        hours_back: Number of hours to look back
        api_key: NASA FIRMS API key
        
    Returns:
        Dictionary containing nearby hotspots
        
    Raises:
        HotspotDetectionError: When detection fails
        ValueError: When coordinates are invalid
    """
    try:
        # Validate coordinates
        center = Coordinates(latitude=lat, longitude=lng)
        
        # Calculate bounding box (rough approximation)
        # 1 degree ≈ 111 km at equator
        degree_offset = radius_km / 111.0
        
        zone_bounds = {
            'north': min(90, lat + degree_offset),
            'south': max(-90, lat - degree_offset),
            'east': min(180, lng + degree_offset),
            'west': max(-180, lng - degree_offset)
        }
        
        # Get hotspots in the bounding box
        result = get_active_hotspots(
            zone_bounds=zone_bounds,
            hours_back=hours_back,
            api_key=api_key
        )
        
        # Filter by actual distance and apply limit
        if 'hotspots' in result:
            nearby_hotspots = []
            for hotspot_data in result['hotspots']:
                hotspot = Hotspot(**hotspot_data)
                distance = _calculate_distance(
                    lat, lng, hotspot.latitude, hotspot.longitude
                )
                if distance <= radius_km:
                    nearby_hotspots.append(hotspot_data)
                    if len(nearby_hotspots) >= limit:
                        break
            
            result['hotspots'] = nearby_hotspots
            result['total_count'] = len(nearby_hotspots)
        
        return result
        
    except Exception as e:
        logger.error(f"Nearby hotspot search failed: {str(e)}")
        raise HotspotDetectionError(f"Failed to find nearby hotspots: {str(e)}")

def _fetch_hotspots_from_source(
    bounds: ZoneBounds,
    time_range: TimeRange,
    source: str,
    min_confidence: int,
    api_key: str
) -> List[Hotspot]:
    """
    Fetch hotspots from a specific data source.
    
    Args:
        bounds: Zone boundaries
        time_range: Time range for query
        source: Data source name
        min_confidence: Minimum confidence threshold
        api_key: API key for authentication
        
    Returns:
        List of Hotspot objects
        
    Raises:
        APIConnectionError: When API request fails
    """
    try:
        # For now, return mock data since we don't have real API keys
        # In production, this would make actual API calls to NASA FIRMS
        
        mock_hotspots = [
            Hotspot(
                id=uuid4(),
                latitude=bounds.south + (bounds.north - bounds.south) * 0.3,
                longitude=bounds.west + (bounds.east - bounds.west) * 0.4,
                timestamp=datetime.now() - timedelta(hours=2),
                confidence=85,
                frp=12.5,
                source=HotspotSource(source),
                metadata=HotspotMetadata(
                    satellite="NOAA-20" if source == "VIIRS" else "Terra",
                    scan_angle=15.2,
                    pixel_size=375 if source == "VIIRS" else 1000,
                    brightness_temp=320.5
                )
            ),
            Hotspot(
                id=uuid4(),
                latitude=bounds.south + (bounds.north - bounds.south) * 0.7,
                longitude=bounds.west + (bounds.east - bounds.west) * 0.6,
                timestamp=datetime.now() - timedelta(hours=1),
                confidence=92,
                frp=25.8,
                source=HotspotSource(source),
                metadata=HotspotMetadata(
                    satellite="NOAA-20" if source == "VIIRS" else "Aqua",
                    scan_angle=8.7,
                    pixel_size=375 if source == "VIIRS" else 1000,
                    brightness_temp=335.2
                )
            )
        ]
        
        return [h for h in mock_hotspots if h.confidence >= min_confidence]
        
    except Exception as e:
        logger.error(f"Failed to fetch from {source}: {str(e)}")
        raise APIConnectionError(f"API request failed for {source}: {str(e)}")

def _remove_duplicate_hotspots(hotspots: List[Hotspot]) -> List[Hotspot]:
    """
    Remove duplicate hotspots based on proximity and time.
    
    Args:
        hotspots: List of hotspot objects
        
    Returns:
        List of unique hotspots
    """
    if not hotspots:
        return []
    
    unique_hotspots = []
    for hotspot in hotspots:
        is_duplicate = False
        for existing in unique_hotspots:
            # Consider duplicates if within 1km and 1 hour
            distance = _calculate_distance(
                hotspot.latitude, hotspot.longitude,
                existing.latitude, existing.longitude
            )
            time_diff = abs((hotspot.timestamp - existing.timestamp).total_seconds())
            
            if distance < 1.0 and time_diff < 3600:  # 1km, 1 hour
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_hotspots.append(hotspot)
    
    return unique_hotspots

def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points in kilometers.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        Distance in kilometers
    """
    from math import radians, cos, sin, asin, sqrt
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r
