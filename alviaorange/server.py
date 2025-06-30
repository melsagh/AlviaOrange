"""Enhanced HTTP server for AlviaOrange API with comprehensive wildfire monitoring endpoints."""

from __future__ import annotations

import os
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import math

from fastapi import FastAPI, HTTPException, Depends, Query, Path, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, Response
from pydantic import BaseModel, Field, validator
import uvicorn

from .hotspots import (
    fetch_hotspots,
    detect_hotspots_for_zone,
    get_active_hotspots,
    get_hotspots_near_point
)
from .air_quality import (
    fetch_air_quality,
    fetch_aqi_scale,
    fetch_air_quality_history,
)
from .cwfis import (
    fetch_fire_weather_index as fetch_fwi_cwfis,
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
from .weather_stations import (
    fetch_climate_stations,
    find_nearest_stations,
    get_station_weather_data,
    weather_station_workflow
)
from .schemas import (
    APIResponse, ErrorResponse, Coordinates, ZoneBounds,
    RiskLevel, RiskAssessment, Hotspot, HotspotQueryResult
)
from .example_implementation import (
    fetch_nasa_firms_hotspots,
    fetch_openweather_forecast,
    fetch_openweather_current,
    fetch_fire_weather_index as fetch_fwi_from_calculator,
    fetch_owm_fwi,
    fetch_fwi_tile_from_owm,
    assess_fire_danger_risk,
    fetch_climate_stations_from_ec,
    fetch_climate_normals_from_ec,
    fetch_aq_history_by_coords
)
from .analysis import (
    calculate_drought_index,
    calculate_fuel_moisture_timeseries,
    get_fwi_anomaly
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
API_VERSION = "2.1.0"
API_TITLE = "AlviaOrange Wildfire Monitoring API"
API_DESCRIPTION = "Comprehensive wildfire monitoring and risk assessment API"

# Rate limiting storage (in production, use Redis)
rate_limit_store: Dict[str, List[float]] = {}
RATE_LIMIT_REQUESTS = 1000
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class BBox(BaseModel):
    """Bounding box for spatial queries."""
    lng_min: float = Field(..., ge=-180, le=180)
    lat_min: float = Field(..., ge=-90, le=90)
    lng_max: float = Field(..., ge=-180, le=180)
    lat_max: float = Field(..., ge=-90, le=90)
    
    @validator('lng_max')
    def lng_max_greater_than_min(cls, v, values):
        if 'lng_min' in values and v <= values['lng_min']:
            raise ValueError('lng_max must be greater than lng_min')
        return v
    
    @validator('lat_max')
    def lat_max_greater_than_min(cls, v, values):
        if 'lat_min' in values and v <= values['lat_min']:
            raise ValueError('lat_max must be greater than lat_min')
        return v

class HealthStatus(BaseModel):
    """System health status."""
    status: str
    timestamp: datetime
    version: str
    database_connected: bool
    external_services: Dict[str, bool]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_api_key(x_api_key: str = Header(None)) -> str:
    """Validate API key from request headers."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    valid_keys = os.getenv("VALID_API_KEYS", "demo-key,test-key").split(",")
    if x_api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return x_api_key

def check_rate_limit(api_key: str, request: Request) -> None:
    """Check rate limiting for API key."""
    now = time.time()
    client_host = request.client.host if request.client else "unknown"
    client_id = f"{api_key}:{client_host}"
    
    if client_id not in rate_limit_store:
        rate_limit_store[client_id] = []
    
    rate_limit_store[client_id] = [
        req_time for req_time in rate_limit_store[client_id]
        if now - req_time < RATE_LIMIT_WINDOW
    ]
    
    if len(rate_limit_store[client_id]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    rate_limit_store[client_id].append(now)

def parse_bbox(bbox: str) -> BBox:
    """Parse bbox string to BBox object."""
    try:
        parts = bbox.split(',')
        if len(parts) != 4:
            raise ValueError("bbox must have 4 comma-separated values")
        
        lng_min, lat_min, lng_max, lat_max = map(float, parts)
        return BBox(lng_min=lng_min, lat_min=lat_min, lng_max=lng_max, lat_max=lat_max)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid bbox format: {str(e)}")

def create_spatial_metadata(bbox: Optional[BBox], count: int = 0) -> Dict[str, Any]:
    """Create spatial metadata for responses."""
    metadata = {
        "spatial_reference": "EPSG:4326",
        "total_count": count
    }
    
    if bbox:
        metadata["bbox"] = {
            "sw": {"lat": bbox.lat_min, "lng": bbox.lng_min},
            "ne": {"lat": bbox.lat_max, "lng": bbox.lng_max}
        }
    
    return metadata

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/api/orange/docs",
    redoc_url="/api/orange/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# NEW API ENDPOINTS
# ============================================================================

@app.get("/api/orange/health")
async def health_check() -> HealthStatus:
    """System health check endpoint."""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now(),
        version=API_VERSION,
        database_connected=True,
        external_services={"environment_canada": True, "cwfis": True, "nasa_firms": True}
    )

# ... (Hotspot, Air Quality, Weather endpoints remain the same as previous implementations) ...

@app.get("/api/orange/hotspots", response_model=None)
async def api_get_hotspots(
    request: Request,
    bbox: Optional[str] = Query(None, description="Bounding box: lng_min,lat_min,lng_max,lat_max"),
    days_back: int = Query(1, description="Number of days to look back", ge=1, le=10),
    api_key: str = Depends(validate_api_key)
) -> Union[Dict[str, Any], JSONResponse]:
    check_rate_limit(api_key, request)
    try:
        result = await fetch_nasa_firms_hotspots(bbox=bbox, days_back=days_back)
        if bbox:
            bbox_obj = parse_bbox(bbox)
            result.update(create_spatial_metadata(bbox_obj, result.get('count', 0)))
        return result
    except Exception as e:
        logger.error(f"Hotspot detection failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/orange/hotspots/active", response_model=None)
async def api_get_active_hotspots(
    request: Request,
    api_key: str = Depends(validate_api_key)
) -> Union[Dict[str, Any], JSONResponse]:
    """Get active hotspots."""
    check_rate_limit(api_key, request)
    try:
        result = await fetch_nasa_firms_hotspots(days_back=1)
        result["source"] = "NASA_FIRMS_ACTIVE"
        return result
    except Exception as e:
        logger.error(f"Active hotspot detection failed: {e}")
        return JSONResponse(status_code=503, content={"message": "Could not fetch active hotspots.", "details": str(e)})

@app.get("/api/orange/hotspots/near", response_model=None)
async def api_get_hotspots_near(
    request: Request,
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lng: float = Query(..., description="Longitude", ge=-180, le=180),
    radius: int = Query(50000, description="Radius in meters", ge=1000, le=200000),
    api_key: str = Depends(validate_api_key)
) -> Union[Dict[str, Any], JSONResponse]:
    """Get hotspots near coordinates."""
    check_rate_limit(api_key, request)
    try:
        # Create a bounding box around the point
        # Rough conversion: 1 degree ≈ 111km
        lat_delta = (radius / 111000)
        lng_delta = (radius / (111000 * abs(math.cos(math.radians(lat)))))
        
        bbox = f"{lng-lng_delta},{lat-lat_delta},{lng+lng_delta},{lat+lat_delta}"
        result = await fetch_nasa_firms_hotspots(bbox=bbox, days_back=2)
        result["search_center"] = {"lat": lat, "lng": lng}
        result["search_radius_m"] = radius
        result["source"] = "NASA_FIRMS_NEAR"
        return result
    except Exception as e:
        logger.error(f"Near hotspot detection failed: {e}")
        return JSONResponse(status_code=503, content={"message": "Could not fetch nearby hotspots.", "details": str(e)})

@app.get("/api/orange/air-quality/history", response_model=None)
async def api_get_air_quality_history(
    request: Request,
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lng: float = Query(..., description="Longitude", ge=-180, le=180),
    start: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end: str = Query(..., description="End date in YYYY-MM-DD format"),
    api_key: str = Depends(validate_api_key)
) -> Union[Dict[str, Any], JSONResponse]:
    check_rate_limit(api_key, request)
    try:
        datetime.fromisoformat(start)
        datetime.fromisoformat(end)
        result = await fetch_aq_history_by_coords(lat=lat, lng=lng, start_date=start, end_date=end)
        return result
    except Exception as e:
        logger.error(f"Air quality history failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
        
# ... [Other endpoints like /weather/forecast, /fire-danger/rating, etc.] ...


# ============================================================================
# ANALYSIS PRIMITIVES (NEWLY ADDED)
# ============================================================================

@app.get("/api/orange/analysis/drought", response_model=None)
async def api_get_drought_index(
    request: Request,
    station_id: str = Query(..., description="Climate station identifier"),
    year: int = Query(..., description="Year for analysis", ge=1900, le=2100),
    month: int = Query(..., description="Month for analysis", ge=1, le=12),
    api_key: str = Depends(validate_api_key)
) -> Union[Dict[str, Any], JSONResponse]:
    """
    Calculate a simplified drought index based on precipitation anomaly.
    """
    check_rate_limit(api_key, request)
    try:
        result = calculate_drought_index(station_id=station_id, year=year, month=month)
        if "error" in result:
             return JSONResponse(status_code=404, content={"message": result["error"]})
        return result
    except Exception as e:
        logger.error(f"Drought index endpoint failed: {e}")
        return JSONResponse(status_code=500, content={"message": "Could not perform drought analysis.", "details": str(e)})


@app.get("/api/orange/analysis/fuel-moisture", response_model=None)
async def api_get_fuel_moisture(
    request: Request,
    station_id: str = Query(..., description="Climate station identifier"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    api_key: str = Depends(validate_api_key)
) -> Union[Dict[str, Any], JSONResponse]:
    """
    Calculate daily fuel moisture (FFMC, DMC) for a given period.
    """
    check_rate_limit(api_key, request)
    try:
        datetime.fromisoformat(start_date)
        datetime.fromisoformat(end_date)
        result = calculate_fuel_moisture_timeseries(station_id, start_date, end_date)
        if "error" in result:
             return JSONResponse(status_code=404, content={"message": result["error"]})
        return result
    except ValueError:
        return JSONResponse(status_code=400, content={"message": "Invalid date format. Use YYYY-MM-DD."})
    except Exception as e:
        logger.error(f"Fuel moisture endpoint failed: {e}")
        return JSONResponse(status_code=500, content={"message": "Could not calculate fuel moisture.", "details": str(e)})


@app.get("/api/orange/analysis/fwi-anomaly", response_model=None)
async def api_get_fwi_anomaly(
    request: Request,
    station_id: str = Query(..., description="Climate station identifier"),
    date: str = Query(..., description="Date for analysis in YYYY-MM-DD format"),
    api_key: str = Depends(validate_api_key)
) -> Union[Dict[str, Any], JSONResponse]:
    """
    Calculates the FWI anomaly, comparing a day's FWI to the long-term normal.
    """
    check_rate_limit(api_key, request)
    try:
        datetime.fromisoformat(date)
        result = get_fwi_anomaly(station_id=station_id, date_str=date)
        if "error" in result:
             return JSONResponse(status_code=404, content={"message": result["error"]})
        return result
    except ValueError:
        return JSONResponse(status_code=400, content={"message": "Invalid date format. Use YYYY-MM-DD."})
    except Exception as e:
        logger.error(f"FWI anomaly endpoint failed: {e}")
        return JSONResponse(status_code=500, content={"message": "Could not calculate FWI anomaly.", "details": str(e)})

# ============================================================================
# WEATHER DATA ENDPOINTS
# ============================================================================

@app.get("/api/orange/weather/forecast", response_model=None)
async def api_get_weather_forecast(
    request: Request,
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lng: float = Query(..., description="Longitude", ge=-180, le=180),
    days: int = Query(7, description="Number of forecast days", ge=1, le=14),
    api_key: str = Depends(validate_api_key)
) -> Union[Dict[str, Any], JSONResponse]:
    """Get weather forecast for a specific location."""
    check_rate_limit(api_key, request)
    try:
        result = await fetch_openweather_forecast(lat=lat, lng=lng, days=days)
        return result
    except Exception as e:
        logger.error(f"Weather forecast endpoint failed: {e}")
        return JSONResponse(status_code=503, content={"message": "Could not fetch weather forecast.", "details": str(e)})

@app.get("/api/orange/weather/current", response_model=None)
async def api_get_current_weather(
    request: Request,
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lng: float = Query(..., description="Longitude", ge=-180, le=180),
    api_key: str = Depends(validate_api_key)
) -> Union[Dict[str, Any], JSONResponse]:
    """Get current weather for a specific location."""
    check_rate_limit(api_key, request)
    try:
        result = await fetch_openweather_current(lat=lat, lng=lng)
        return result
    except Exception as e:
        logger.error(f"Current weather endpoint failed: {e}")
        return JSONResponse(status_code=503, content={"message": "Could not fetch current weather.", "details": str(e)})

@app.get("/api/orange/weather/fire-index", response_model=None)
async def api_get_fire_weather_index(
    request: Request,
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lng: float = Query(..., description="Longitude", ge=-180, le=180),
    source: str = Query("calculator", description="FWI data source ('calculator' or 'openweathermap')"),
    api_key: str = Depends(validate_api_key)
) -> Union[Dict[str, Any], JSONResponse]:
    """Get Fire Weather Index for a location."""
    check_rate_limit(api_key, request)
    try:
        if source == "openweathermap":
            result = await fetch_owm_fwi(lat=lat, lng=lng)
        else:
            result = await fetch_fwi_from_calculator(lat=lat, lng=lng)
        return result
    except Exception as e:
        logger.error(f"FWI endpoint failed: {e}")
        return JSONResponse(status_code=503, content={"message": "Could not calculate Fire Weather Index.", "details": str(e)})

# ============================================================================
# AIR QUALITY ENDPOINTS  
# ============================================================================

@app.get("/api/orange/air-quality", response_model=None)
async def api_get_air_quality(
    request: Request,
    api_key: str = Depends(validate_api_key)
) -> Dict[str, Any]:
    """Get basic air quality data."""
    check_rate_limit(api_key, request)
    return {
        "source": "AlviaOrange Basic AQ",
        "message": "Basic air quality endpoint - upgrade to coordinate-specific history",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/orange/air-quality/scale", response_model=None)
async def api_get_air_quality_scale(
    request: Request,
    api_key: str = Depends(validate_api_key)
) -> Dict[str, Any]:
    """Get air quality scale definitions."""
    check_rate_limit(api_key, request)
    return {
        "source": "AlviaOrange AQ Scale",
        "scales": [{
            "name": "AQI",
            "ranges": [
                {"min": 0, "max": 50, "level": "Good", "color": "#00e400"},
                {"min": 51, "max": 100, "level": "Moderate", "color": "#ffff00"},
                {"min": 101, "max": 150, "level": "Unhealthy for Sensitive Groups", "color": "#ff7e00"},
                {"min": 151, "max": 200, "level": "Unhealthy", "color": "#ff0000"},
                {"min": 201, "max": 300, "level": "Very Unhealthy", "color": "#8f3f97"},
                {"min": 301, "max": 500, "level": "Hazardous", "color": "#7e0023"}
            ]
        }]
    }

# ============================================================================
# CLIMATE DATA ENDPOINTS
# ============================================================================

@app.get("/api/orange/climate/stations", response_model=None)
async def api_get_climate_stations(
    request: Request,
    bbox: Optional[str] = Query(None, description="Bounding box filter: lng_min,lat_min,lng_max,lat_max"),
    api_key: str = Depends(validate_api_key)
) -> Union[Dict[str, Any], JSONResponse]:
    """Get a list of climate stations, with optional bounding box filter."""
    check_rate_limit(api_key, request)
    try:
        stations = await fetch_climate_stations_from_ec(bbox=bbox)
        return {"source": "Environment Canada", "stations": stations}
    except Exception as e:
        logger.error(f"Climate stations endpoint failed: {e}")
        return JSONResponse(status_code=503, content={"message": "Could not fetch climate stations.", "details": str(e)})

@app.get("/api/orange/climate/normals", response_model=None)
async def api_get_climate_normals(
    request: Request,
    station_id: str = Query(..., description="Station identifier"),
    period: str = Query("1981-2010", description="Climate normal period"),
    api_key: str = Depends(validate_api_key)
) -> Union[Dict[str, Any], JSONResponse]:
    """Get climate normals for a specific station."""
    check_rate_limit(api_key, request)
    try:
        result = await fetch_climate_normals_from_ec(station_id=station_id, period=period)
        return result
    except Exception as e:
        logger.error(f"Climate normals endpoint failed: {e}")
        return JSONResponse(status_code=503, content={"message": "Could not fetch climate normals.", "details": str(e)})

# ============================================================================
# WMS TILE ENDPOINTS
# ============================================================================

@app.get("/api/orange/wms/tiles/{z}/{x}/{y}", response_model=None)
async def api_get_wms_tile(
    request: Request,
    z: int = Path(..., description="Zoom level"),
    x: int = Path(..., description="Tile X coordinate"),
    y: int = Path(..., description="Tile Y coordinate"),
    layer: str = Query("fire-danger", description="Layer name"),
    api_key: str = Depends(validate_api_key)
) -> Response:
    """Get a WMS tile for fire danger visualization."""
    check_rate_limit(api_key, request)
    try:
        if layer == "fire-danger":
            tile_data = await fetch_fwi_tile_from_owm(z=z, x=x, y=y)
            return Response(content=tile_data, media_type="image/png")
        else:
            return JSONResponse(status_code=400, content={"message": f"Unsupported layer: {layer}"})
    except Exception as e:
        logger.error(f"WMS tile endpoint failed: {e}")
        return JSONResponse(status_code=503, content={"message": "Could not fetch map tile.", "details": str(e)})

# ============================================================================
# LEGACY ENDPOINTS (Maintained for backward compatibility)
# ============================================================================

@app.get("/hotspots", include_in_schema=False)
def get_legacy_hotspots(region: str = "Canada"):
    return fetch_hotspots(region)

@app.get("/air_quality", include_in_schema=False)
def get_legacy_air_quality():
    return fetch_air_quality()

# ... [Add other legacy endpoints here if needed] ...
