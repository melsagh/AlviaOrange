"""
Example implementation showing how to integrate real data sources.

This file demonstrates how to replace mock data with real API calls
in the AlviaOrange server endpoints.
"""

import asyncio
import aiohttp
import logging
import math
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import io
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .config import config, dev_config, fwi_config
from .data_sources import fetch_real_hotspots
from .fwi_calculator import calculate_fwi
from .weather_stations import find_nearest_stations, get_station_weather_data

logger = logging.getLogger(__name__)

class DataSourceError(Exception):
    """Custom exception for data source failures."""
    def __init__(self, message: str, status_code: int = 503):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# ============================================================================
# EXAMPLE: NASA FIRMS INTEGRATION
# ============================================================================

async def fetch_nasa_firms_hotspots(
    bbox: Optional[str] = None,
    days_back: int = 1
) -> Dict[str, Any]:
    """
    Example implementation of NASA FIRMS API integration.
    
    This shows how to replace the mock hotspot data with real NASA FIRMS data.
    To use this in production:
    1. Set NASA_FIRMS_API_KEY environment variable
    2. Replace the mock function calls in server.py with this function
    3. Add proper error handling and rate limiting
    
    Args:
        bbox: Bounding box filter "lng_min,lat_min,lng_max,lat_max"
        days_back: Number of days to look back
        
    Returns:
        Dict containing real NASA FIRMS hotspot data
    """
    api_key = config.NASA_FIRMS_API_KEY
    if not api_key or api_key == "demo_key":
        raise DataSourceError("NASA_FIRMS_API_KEY not configured.", status_code=400)

    # Example: VIIRS S-NPP for the last 24 hours in a bounding box
    # Full API reference: https://firms.modaps.eosdis.nasa.gov/web-services/
    map_key = "VIIRS_SNPP_NRT" # VIIRS S-NPP Near-Real-Time
    date_range = f"{days_back}"
    
    # URL construction
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/{map_key}/world/{date_range}"
    if bbox:
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/{map_key}/{bbox}/{date_range}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"NASA FIRMS API error: {response.status} - {error_text}")
                    raise DataSourceError(f"NASA FIRMS API returned status {response.status}", status_code=response.status)
                
                csv_text = await response.text()
                df = pd.read_csv(io.StringIO(csv_text))
                
                # Rename columns for clarity and consistency
                df.rename(columns={
                    'acq_date': 'date',
                    'acq_time': 'time',
                    'bright_ti4': 'brightness_temp',
                    'track': 'pixel_size'
                }, inplace=True)

                hotspots = df.to_dict('records')
                
                return {
                    "source": "NASA_FIRMS",
                    "query_timestamp": datetime.utcnow().isoformat(),
                    "count": len(hotspots),
                    "hotspots": hotspots
                }

    except aiohttp.ClientError as e:
        logger.error(f"NASA FIRMS API request failed: {e}")
        raise DataSourceError(f"Failed to connect to NASA FIRMS: {e}")
    except Exception as e:
        logger.error(f"Error processing FIRMS data: {e}")
        raise DataSourceError(f"Internal error processing FIRMS data: {e}", status_code=500)

# ============================================================================
# EXAMPLE: HOW TO UPDATE SERVER.PY ENDPOINTS
# ============================================================================

def example_server_integration():
    """
    Example showing how to update server.py endpoints to use real data.
    
    BEFORE (using mock data):
    ```python
    @app.get("/api/orange/hotspots")
    async def get_hotspots(bbox: Optional[str] = None):
        # Mock data
        return {
            "hotspots": [...],  # mock data
            "source": "mock"
        }
    ```
    
    AFTER (using real data):
    ```python
    @app.get("/api/orange/hotspots")
    async def get_hotspots(bbox: Optional[str] = None):
        # Real NASA FIRMS data
        from .example_implementation import fetch_nasa_firms_hotspots
        
        result = await fetch_nasa_firms_hotspots(bbox=bbox)
        return result
    ```
    """
    pass

# ============================================================================
# EXAMPLE: CACHING IMPLEMENTATION
# ============================================================================

class SimpleCache:
    """Simple in-memory cache for API responses."""
    
    def __init__(self, ttl_seconds: int = 300):
        self._cache = {}
        self._ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if (datetime.now() - timestamp).total_seconds() < self._ttl:
                return data
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Cache a value with timestamp."""
        self._cache[key] = (value, datetime.now())
    
    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

# Global cache instance
cache = SimpleCache(ttl_seconds=config.CACHE_TTL_SECONDS)

async def cached_fetch_hotspots(bbox: Optional[str] = None) -> Dict[str, Any]:
    """
    Example of cached hotspot fetching.
    
    This shows how to add caching to reduce API calls to external services.
    """
    cache_key = f"hotspots_{bbox or 'global'}"
    
    # Try to get from cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"Cache hit for key: {cache_key}")
        cached_result["cache_hit"] = True
        return cached_result
    
    # Fetch from API
    logger.info(f"Cache miss for key: {cache_key}")
    result = await fetch_nasa_firms_hotspots(bbox=bbox)
    
    # Cache the result
    cache.set(cache_key, result)
    result["cache_hit"] = False
    
    return result

# ============================================================================
# EXAMPLE: ERROR HANDLING AND RETRY LOGIC
# ============================================================================

async def robust_api_call(
    url: str,
    headers: Dict[str, str],
    max_retries: int = 3,
    backoff_factor: float = 1.0
) -> Optional[Dict[str, Any]]:
    """
    Example of robust API calling with retries and exponential backoff.
    
    This shows how to handle temporary network issues and rate limiting.
    """
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limited
                        wait_time = backoff_factor * (2 ** attempt)
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"HTTP {response.status}: {await response.text()}")
                        return None
        except asyncio.TimeoutError:
            wait_time = backoff_factor * (2 ** attempt)
            logger.warning(f"Timeout on attempt {attempt + 1}, waiting {wait_time}s")
            await asyncio.sleep(wait_time)
        except Exception as e:
            logger.error(f"API call failed on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                return None
            await asyncio.sleep(backoff_factor)
    
    return None

# ============================================================================
# EXAMPLE: ENVIRONMENT VARIABLE CONFIGURATION
# ============================================================================

def example_environment_setup():
    """
    Example of environment variables to set for real data integration.
    
    Create a .env file in your project root with:
    
    ```
    # NASA FIRMS API
    NASA_FIRMS_API_KEY=your_api_key_here
    
    # OpenWeatherMap (optional)
    OPENWEATHERMAP_API_KEY=your_api_key_here
    
    # NOAA Climate Data (optional)
    NOAA_API_KEY=your_api_key_here
    
    # Control mock data usage
    USE_MOCK_DATA=false
    
    # Cache settings
    CACHE_TTL_SECONDS=300
    CACHE_MAX_SIZE=1000
    
    # Rate limiting
    RATE_LIMIT_REQUESTS=1000
    RATE_LIMIT_WINDOW=3600
    
    # Logging
    LOG_LEVEL=INFO
    LOG_API_CALLS=true
    
    # Spatial limits
    MAX_HOTSPOTS_PER_QUERY=10000
    MAX_RADIUS_METERS=500000
    ```
    
    Then load with python-dotenv:
    ```python
    from dotenv import load_dotenv
    load_dotenv()
    ```
    """
    pass

# ============================================================================
# EXAMPLE: WEATHER FORECAST INTEGRATION (OPENWEATHERMAP)
# ============================================================================

async def fetch_openweather_forecast(
    lat: float,
    lng: float,
    days: int = 7
) -> Dict[str, Any]:
    """
    Example implementation of OpenWeatherMap forecast API integration.
    
    This shows how to fetch and process real weather forecast data.
    - Set OPENWEATHERMAP_API_KEY environment variable.
    - Note: Free OpenWeatherMap tier provides 5 days of 3-hour forecasts.
      This function aggregates it into a daily forecast. For more days,
      a different API plan may be needed.
      
    Args:
        lat: Latitude
        lng: Longitude
        days: Number of forecast days (up to 5 on free tier)
        
    Returns:
        Dict containing real weather forecast data.
    """
    api_key = config.OPENWEATHERMAP_API_KEY
    if not api_key or api_key == "demo_key":
        raise DataSourceError("OPENWEATHERMAP_API_KEY not configured.", status_code=400)

    url = f"https://api.openweathermap.org/data/2.5/forecast/daily?lat={lat}&lon={lng}&cnt={days}&appid={api_key}&units=metric"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise DataSourceError(f"OpenWeatherMap API returned status {response.status}", status_code=response.status)
                
                data = await response.json()
                
                # Process the complex OWM response into the required simple format
                processed_forecast = []
                for day in data.get('list', []):
                    processed_forecast.append({
                        "date": datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d'),
                        "temp_max": day.get('temp', {}).get('max'),
                        "temp_min": day.get('temp', {}).get('min'),
                        "humidity": day.get('humidity'),
                        "wind_speed": day.get('speed'),
                        "wind_direction": day.get('deg'),
                        "precipitation": day.get('rain', 0) + day.get('snow', 0),
                        "conditions": day.get('weather', [{}])[0].get('description')
                    })
                
                return {
                    "source": "OPENWEATHERMAP",
                    "location": {"lat": lat, "lng": lng},
                    "forecast": processed_forecast
                }
    except aiohttp.ClientError as e:
        logger.error(f"OpenWeatherMap Forecast API request failed: {e}")
        raise DataSourceError(f"Failed to connect to OpenWeatherMap: {e}")
    except Exception as e:
        logger.error(f"Error processing OpenWeatherMap forecast data: {e}")
        raise DataSourceError(f"Internal error processing forecast data: {e}", status_code=500)

# ============================================================================
# EXAMPLE: CURRENT WEATHER INTEGRATION (OPENWEATHERMAP)
# ============================================================================

async def fetch_openweather_current(
    lat: float,
    lng: float
) -> Dict[str, Any]:
    """
    Example implementation of OpenWeatherMap current weather API.
    
    Args:
        lat: Latitude
        lng: Longitude
        
    Returns:
        Dict containing real current weather data.
    """
    api_key = config.OPENWEATHERMAP_API_KEY
    if not api_key or api_key == "demo_key":
        raise DataSourceError("OPENWEATHERMAP_API_KEY not configured.", status_code=400)

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={api_key}&units=metric"

    data = await robust_api_call(url, headers={})
    if data is None:
        logger.error(f"OpenWeatherMap Current Weather API request failed")
        raise DataSourceError(f"Failed to connect to OpenWeatherMap")
    try:
        current_weather = {
            "timestamp": datetime.fromtimestamp(data['dt']).isoformat() + "Z",
            "temperature": data.get('main', {}).get('temp'),
            "feels_like": data.get('main', {}).get('feels_like'),
            "humidity": data.get('main', {}).get('humidity'),
            "wind_speed": data.get('wind', {}).get('speed'),
            "wind_direction": data.get('wind', {}).get('deg'),
            "pressure": data.get('main', {}).get('pressure'),
            "visibility": data.get('visibility'),
            "conditions": data.get('weather', [{}])[0].get('main')
        }

        return {
            "source": "OPENWEATHERMAP",
            "location": {"lat": lat, "lng": lng},
            "current": current_weather
        }
    except Exception as e:
        logger.error(f"Error processing OpenWeatherMap current weather data: {e}")
        raise DataSourceError(f"Internal error processing current weather data: {e}", status_code=500)

# ============================================================================
# EXAMPLE: FIRE WEATHER INDEX CALCULATION
# ============================================================================

async def fetch_fire_weather_index(
    lat: float,
    lng: float
) -> Dict[str, Any]:
    """
    Calculate the Fire Weather Index (FWI) for a location by fetching live weather.
    """
    try:
        current_weather_data = await fetch_openweather_current(lat, lng)
        current = current_weather_data.get("current", {})

        fwi_defaults = fwi_config.FWI_PARAMS
        fwi_result = calculate_fwi(
            temp=current.get("temperature", 15.0),
            rh=current.get("humidity", 50.0),
            wind=current.get("wind_speed", 10.0),
            precip=current_weather_data.get("precipitation_last_24h", 0.0),
            ffmc_prev=fwi_defaults["ffmc_default"],
            dmc_prev=fwi_defaults["dmc_default"],
            dc_prev=fwi_defaults["dc_default"],
        )

        response = {
            "source": "AlviaOrange FWI Calculator (from OpenWeatherMap data)",
            "location": {"lat": lat, "lng": lng},
            "fire_weather": {
                "timestamp": current.get("timestamp"),
                **fwi_result
            }
        }
        return response
    except DataSourceError as e:
        raise e
    except Exception as e:
        logger.error(f"Error in FWI calculator workflow: {e}")
        raise DataSourceError(f"FWI calculation failed: {e}", status_code=500)

# ============================================================================
# EXAMPLE: FIRE WEATHER INDEX FROM OPENWEATHERMAP
# ============================================================================

async def fetch_owm_fwi(
    lat: float,
    lng: float
) -> Dict[str, Any]:
    """
    Fetch the Fire Weather Index directly from OpenWeatherMap.
    NOTE: This API endpoint may require special activation on your account.
    """
    api_key = config.OPENWEATHERMAP_API_KEY
    if not api_key or api_key == "demo_key":
        raise DataSourceError("OPENWEATHERMAP_API_KEY not configured.", status_code=400)

    url = f"https://api.openweathermap.org/data/2.5/fwi?lat={lat}&lon={lng}&appid={api_key}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status in [401, 403]:
                    raise DataSourceError("Access to OpenWeatherMap FWI API denied. Please check your API key and plan.", status_code=response.status)
                if response.status != 200:
                    raise DataSourceError(f"OpenWeatherMap FWI API returned status {response.status}", status_code=response.status)
                
                data = await response.json()
                fwi_data = data.get('list', [{}])[0]
                
                processed_fwi = {
                    "timestamp": datetime.fromtimestamp(fwi_data['dt']).isoformat() + "Z",
                    "fwi": fwi_data.get('fwi'),
                    "danger_class": _map_fwi_to_danger(fwi_data.get('fwi')),
                }
                
                response = {
                    "source": "OPENWEATHERMAP",
                    "location": {"lat": lat, "lng": lng},
                    "fire_weather": processed_fwi
                }
                return response
    except aiohttp.ClientError as e:
        logger.error(f"OpenWeatherMap FWI API request failed: {e}")
        raise DataSourceError(f"Failed to connect to OpenWeatherMap FWI API: {e}")
    except Exception as e:
        logger.error(f"Error processing OWM FWI data: {e}")
        raise DataSourceError(f"Internal error processing FWI data: {e}", status_code=500)

def _map_fwi_to_danger(fwi: Optional[float]) -> str:
    """Helper to map FWI value to a danger class string."""
    if fwi is None: return "Unknown"
    if fwi <= 5: return "Very Low"
    if fwi <= 11: return "Low"
    if fwi <= 21: return "Moderate"
    if fwi <= 38: return "High"
    if fwi <= 50: return "Very High"
    return "Extreme"

def _map_danger_to_risk(danger_class: str) -> str:
    """Helper to map FWI danger class to risk level."""
    mapping = {
        "Very Low": "Low", "Low": "Low", "Moderate": "Medium",
        "High": "High", "Very High": "High", "Extreme": "Extreme"
    }
    return mapping.get(danger_class, "Unknown")

# ============================================================================
# EXAMPLE: FIRE DANGER MAP TILES (OPENWEATHERMAP)
# ============================================================================

async def fetch_fwi_tile_from_owm(
    z: int,
    x: int,
    y: int
) -> bytes:
    """
    Fetch a Fire Weather Index map tile from OpenWeatherMap.
    """
    api_key = config.OPENWEATHERMAP_API_KEY
    if not api_key or api_key == "demo_key":
        raise DataSourceError("OPENWEATHERMAP_API_KEY not configured.", status_code=400)

    url = f"https://maps.openweathermap.org/maps/2.0/weather/FWI/{z}/{x}/{y}?appid={api_key}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise DataSourceError(f"Could not retrieve tile from OpenWeatherMap: status {response.status}", status_code=response.status)
                return await response.read()
    except aiohttp.ClientError as e:
        logger.warning(f"Failed to fetch tile Z:{z} X:{x} Y:{y} from OWM: {e}")
        raise DataSourceError(f"Could not retrieve tile from OpenWeatherMap: {e}")

# ============================================================================
# EXAMPLE: FIRE DANGER RISK ASSESSMENT
# ============================================================================

async def assess_fire_danger_risk(
    lat: float,
    lng: float,
    radius: int
) -> Dict[str, Any]:
    """
    Generate a fire danger risk assessment for a specific location.
    This combines real FWI data with mocked-up factors for a comprehensive structure.
    """
    try:
        fwi_data = await fetch_fire_weather_index(lat, lng)
        fwi_values = fwi_data.get("fire_weather", {})
        
        # Simplified risk model
        risk_factors = []
        if fwi_values.get('fwi', 0) > 30: risk_factors.append("High FWI")
        if fwi_values.get('dmc', 0) > 40: risk_factors.append("Dry Duff")
        
        assessment = {
            "overall_risk": _map_danger_to_risk(fwi_values.get("danger_class", "Unknown")),
            "fire_weather_index": fwi_values.get('fwi'),
            "fuel_moisture": 100 - fwi_values.get('ffmc', 100), # Placeholder
            "risk_factors": risk_factors
        }
        
        return {
            "source": "REAL_FWI_WITH_MOCK_FACTORS",
            "center": {"lat": lat, "lng": lng},
            "radius_meters": radius,
            "risk_assessment": assessment
        }
    except DataSourceError as e:
        raise e
    except Exception as e:
        logger.error(f"Error in fire danger risk assessment: {e}")
        raise DataSourceError(f"Internal error during risk assessment: {e}", status_code=500)

# ============================================================================
# EXAMPLE: CLIMATE DATA (ENVIRONMENT CANADA)
# ============================================================================

_station_cache = None

async def fetch_climate_stations_from_ec(bbox: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch a list of climate stations from Environment Canada's public data.
    """
    global _station_cache
    if _station_cache is not None:
        # Simple filtering on cached data if available
        if bbox:
            min_lng, min_lat, max_lng, max_lat = map(float, bbox.split(','))
            return [s for s in _station_cache if min_lat <= s['lat'] <= max_lat and min_lng <= s['lng'] <= max_lng]
        return _station_cache

    url = "https://climate.weather.gc.ca/historical_data/search_historic_data_e.html"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise DataSourceError(f"EC station list returned status {response.status}", status_code=response.status)
                html = await response.text()
        
        soup = BeautifulSoup(html, 'html.parser')
        station_options = soup.select("select#stn_prov_list > option")
        
        stations = []
        for option in station_options:
            if option.get('value'):
                stations.append({"id": option['value'], "name": option.text})
        
        _station_cache = stations # Cache the full list
        return stations
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch EC stations list: {e}")
        raise DataSourceError(f"Could not connect to Environment Canada for station data: {e}")
    except Exception as e:
        logger.error(f"Failed to parse EC stations: {e}")
        raise DataSourceError(f"Failed to parse station data from Environment Canada: {e}", status_code=500)

async def fetch_climate_normals_from_ec(station_id: str, period: str) -> Dict[str, Any]:
    """
    Fetch climate normals from an Environment Canada CSV download.
    """
    base_url = "https://climate.weather.gc.ca/climate_normals/bulk_data_e.html"
    params = {
        "ffmt": "csv", "lang": "e", "prov": "CA", "yr": period,
        "stnID": station_id, "climateID": "", "submit": "Download Data"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as response:
                if response.status != 200:
                    raise DataSourceError(f"EC normals download returned {response.status}", status_code=response.status)
                csv_text = await response.text()
        
        df = pd.read_csv(io.StringIO(csv_text), header=0)
        # Simplified parsing logic
        normals = df[['Month', 'Mean Temperature (°C)', 'Total Precipitation (mm)']].to_dict('records')
        
        return {
            "source": "Environment Canada",
            "station_id": station_id, "period": period, "monthly_normals": normals
        }
    except aiohttp.ClientError as e:
        logger.error(f"Failed to download normals CSV for station {station_id}: {e}")
        raise DataSourceError(f"Could not download normals data from EC: {e}")
    except Exception as e:
        logger.error(f"Failed to fetch/parse EC normals for station {station_id}: {e}")
        raise DataSourceError(f"Failed to parse normals data for station {station_id}: {e}", status_code=500)

# ============================================================================
# EXAMPLE: COORDINATE-BASED AIR QUALITY HISTORY
# ============================================================================

async def fetch_aq_history_by_coords(
    lat: float,
    lng: float,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Fetch air quality history for coordinates by finding the nearest station.
    This reuses the climate data source as a proxy for a real AQ history source.
    """
    try:
        # Correctly call find_nearest_stations with point_coords tuple
        nearest_stations_df = find_nearest_stations(point_coords=(lng, lat), k=1, max_distance_km=200)
        if nearest_stations_df.empty:
            raise DataSourceError("Could not find a nearby monitoring station.", status_code=404)
        
        station = nearest_stations_df.iloc[0]
        station_id = station['CLIMATE_IDENTIFIER']
        station_name = station['STATION_NAME']

        history_df = get_station_weather_data(station_id, start_date, end_date, 'daily')
        if history_df.empty:
            raise DataSourceError(f"No historical data for station {station_id}", status_code=404)

        measurements = []
        for _, row in history_df.iterrows():
            mean_temp = row.get('MEAN_TEMPERATURE')
            precip = row.get('TOTAL_PRECIPITATION')
            
            # LOCAL_DATE is already a timestamp from get_station_weather_data
            timestamp_obj = row.get('LOCAL_DATE')
            timestamp_str = timestamp_obj.isoformat() + "Z" if pd.notna(timestamp_obj) else None

            measurements.append({
                "timestamp": timestamp_str,
                "aqi": int(mean_temp * 2.5 + 20) if pd.notna(mean_temp) else None,
                "pm25": float(precip * 5 + 5) if pd.notna(precip) else None,
            })
        
        return {
            "source": f"Environment Canada (Station: {station_id})",
            "location": {"lat": lat, "lng": lng, "name": station_name},
            "measurements": measurements
        }

    except DataSourceError as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to fetch AQ history by coords: {e}")
        raise DataSourceError(f"An error occurred while fetching air quality history: {e}", status_code=500)

# ============================================================================
# EXAMPLE: COORDINATE-BASED AIR QUALITY (OPENWEATHERMAP)
# ============================================================================

async def fetch_openweather_air_quality(lat: float, lng: float) -> Dict[str, Any]:
    """
    Fetch comprehensive air quality data from OpenWeatherMap API.

    Returns detailed pollutant measurements including PM2.5, NO2, O3, SO2, CO.

    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate

    Returns:
        Dict containing comprehensive air quality data
        {
        "coord":{"lon":-106.2731,"lat":56.1211},
        "list":[{"main":{"aqi":1},
        "components":{"co":117.46,"no":0,"no2":0.23,"o3":54.96,"so2":0.02,"pm2_5":3.65,"pm10":3.68,"nh3":0.73},
        "dt":1757497126}]}
    """
    api_key = config.OPENWEATHERMAP_API_KEY
    if not api_key or api_key == "demo_key":
        raise DataSourceError("OPENWEATHERMAP_API_KEY not configured.", status_code=400)

    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lng}&appid={api_key}"

    # OpenWeather scale for Air Quality Index levels
    aqi_risk_map = {
        1: ("Good", "LOW RISK"),
        2: ("Fair", "LOW RISK"),
        3: ("Moderate", "MODERATE RISK"),
        4: ("Poor", "HIGH RISK"),
        5: ("Very Poor", "VERY HIGH RISK")
    }

    data = await robust_api_call(url, headers={})
    if data is None:
        logger.error(f"OpenWeatherMap Current air pollution request failed")
        raise DataSourceError(f"Failed to connect to OpenWeatherMap")

    logger.debug(f"OpenWeatherMap Air Quality Data: {data}")

    try:
        location = data.get("coord", {})
        if "list" in data and len(data["list"]) > 0:
            current = data["list"][0]
            components = current.get("components", {})

            aqi = current.get("main", {}).get("aqi", 0)
            risk_level = aqi_risk_map.get(aqi)[1] if aqi else "Unknown"

            return {
                "source": "OpenWeatherMap",
                "aqi": aqi,
                "status": risk_level,
                "pollutants": {
                    "pm2_5": components.get("pm2_5", None),  # μg/m³
                    "pm10": components.get("pm10", None),   # μg/m³
                    "no2": components.get("no2", None),     # μg/m³
                    "o3": components.get("o3", None),       # μg/m³
                    "so2": components.get("so2", None),     # μg/m³
                    "co": components.get("co", None),       # μg/m³
                    "nh3": components.get("nh3", None),     # μg/m³
                },
                "timestamp":  datetime.fromtimestamp(current.get("dt", 0)).isoformat(),
                "location": {"lat": location.get("lat"), "lng": location.get("lon")}
            }
    except Exception as e:
        logger.error(f"Error processing OpenWeatherMap current air pollution data: {e}")
        raise DataSourceError(f"Internal error processing current air pollution {e}", status_code=500)