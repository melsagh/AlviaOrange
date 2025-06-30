# AlviaOrange Real Data Implementation Guide

This guide explains how to implement the skeleton functions in `alviaorange/data_sources.py` to replace mock data with real external data sources.

## Quick Start

1. **Install additional dependencies:**
   ```bash
   pip install aiohttp python-dotenv
   ```

2. **Set up environment variables:**
   Create a `.env` file in your project root:
   ```env
   NASA_FIRMS_API_KEY=your_api_key_here
   OPENWEATHERMAP_API_KEY=your_api_key_here
   USE_MOCK_DATA=false
   ```

3. **Load environment variables in your application:**
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

## Implementation Priority

### High Priority (Essential for Fire Monitoring)
1. **NASA FIRMS Hotspot Integration** - Real fire/hotspot data
2. **Weather API Integration** - Real weather data for fire weather calculations
3. **Fire Weather Index Calculation** - Critical for fire danger assessment

### Medium Priority (Enhanced Features)
4. **Enhanced Air Quality Coordinate Lookup** - Improve existing air quality system
5. **Spatial Database Integration** - For efficient hotspot queries
6. **Caching System** - Reduce API calls and improve performance

### Low Priority (Advanced Features)
7. **Geospatial Tile Services** - Map tile generation
8. **Zone Monitoring System** - Custom zone-based monitoring
9. **Climate Data Integration** - Historical climate analysis

## Detailed Implementation Instructions

### 1. NASA FIRMS Hotspot Integration

**Function:** `fetch_real_hotspots()`

**Implementation Steps:**

1. **Get NASA FIRMS API Key:**
   - Visit https://firms.modaps.eosdis.nasa.gov/api/
   - Register for a free API key
   - Set `NASA_FIRMS_API_KEY` environment variable

2. **Implementation:**
   ```python
   import aiohttp
   from datetime import datetime, timedelta
   
   async def fetch_real_hotspots(bbox: Optional[str] = None) -> Dict[str, Any]:
       api_key = config.NASA_FIRMS_API_KEY
       base_url = "https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/FIRMS"
       
       # Use VIIRS data for most recent satellite imagery
       dataset = "VIIRS_SNPP_NRT"
       
       # Get data from last 24 hours
       end_date = datetime.now()
       start_date = end_date - timedelta(days=1)
       date_range = f"{start_date.strftime('%Y-%m-%d')},{end_date.strftime('%Y-%m-%d')}"
       
       if bbox:
           url = f"{base_url}/{dataset}/c6/area/{bbox}/{date_range}"
       else:
           # Be careful with global queries - large datasets
           url = f"{base_url}/{dataset}/c6/world/{date_range}"
       
       headers = {
           "Authorization": f"Bearer {api_key}",
           "Accept": "application/json"
       }
       
       async with aiohttp.ClientSession() as session:
           async with session.get(url, headers=headers) as response:
               if response.status == 200:
                   data = await response.json()
                   # Process and return data
                   return process_firms_data(data)
               else:
                   # Handle errors, fall back to mock data
                   return fallback_response()
   ```

3. **Data Processing:**
   - Transform NASA FIRMS format to your internal format
   - Handle confidence levels (low, nominal, high)
   - Include fire radiative power (FRP) measurements
   - Filter by acquisition time if needed

4. **Testing:**
   ```python
   # Test with a small bounding box
   bbox = "-80.0,43.0,-79.0,44.0"  # Toronto area
   result = await fetch_real_hotspots(bbox=bbox)
   assert result["source"] == "NASA_FIRMS"
   ```

### 2. Weather API Integration

**Functions:** `fetch_real_weather_forecast()`, `fetch_real_current_weather()`

**Options:**
- **Environment Canada** (Free, Canadian data)
- **OpenWeatherMap** (Freemium, global data)
- **NOAA** (Free, US data)

**Recommended: OpenWeatherMap for simplicity**

1. **Get API Key:**
   - Visit https://openweathermap.org/api
   - Sign up for free tier (1000 calls/day)
   - Set `OPENWEATHERMAP_API_KEY` environment variable

2. **Implementation:**
   ```python
   async def fetch_real_weather_forecast(lat: float, lng: float, days: int = 7) -> Dict[str, Any]:
       api_key = config.OPENWEATHERMAP_API_KEY
       base_url = "https://api.openweathermap.org/data/2.5"
       
       # Get forecast data
       url = f"{base_url}/forecast?lat={lat}&lon={lng}&appid={api_key}&units=metric"
       
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as response:
               if response.status == 200:
                   data = await response.json()
                   return process_weather_forecast(data, days)
               else:
                   return fallback_weather_data()
   ```

3. **Fire Weather Parameters:**
   Focus on these parameters for fire weather:
   - Temperature (°C)
   - Relative Humidity (%)
   - Wind Speed (km/h)
   - Wind Direction (degrees)
   - Precipitation (mm)

### 3. Fire Weather Index (FWI) Calculation

**Function:** `fetch_real_fire_weather_index()`

**Implementation Steps:**

1. **Get Weather Data:**
   Use your implemented weather functions to get current conditions

2. **Implement FWI Formulas:**
   ```python
   def calculate_fwi(temperature: float, humidity: float, wind_speed: float, 
                    precipitation: float, ffmc_prev: float, dmc_prev: float, 
                    dc_prev: float) -> Dict[str, float]:
       """
       Calculate Canadian Fire Weather Index components.
       
       Reference: https://cwfis.cfs.nrcan.gc.ca/background/summary/fwi
       """
       # Fine Fuel Moisture Code (FFMC)
       ffmc = calculate_ffmc(temperature, humidity, wind_speed, precipitation, ffmc_prev)
       
       # Duff Moisture Code (DMC)  
       dmc = calculate_dmc(temperature, humidity, precipitation, dmc_prev)
       
       # Drought Code (DC)
       dc = calculate_dc(temperature, precipitation, dc_prev)
       
       # Initial Spread Index (ISI)
       isi = calculate_isi(wind_speed, ffmc)
       
       # Buildup Index (BUI)
       bui = calculate_bui(dmc, dc)
       
       # Fire Weather Index (FWI)
       fwi = calculate_fwi_final(isi, bui)
       
       return {
           "ffmc": ffmc,
           "dmc": dmc, 
           "dc": dc,
           "isi": isi,
           "bui": bui,
           "fwi": fwi,
           "danger_class": fwi_config.get_danger_class(fwi)
       }
   ```

3. **FWI Formula Implementation:**
   The Canadian FWI system has specific formulas. You can find detailed implementations in:
   - Environment Canada documentation
   - Research papers on fire weather
   - Existing open-source implementations

### 4. Enhanced Air Quality Coordinate Lookup

**Function:** `fetch_real_air_quality_by_coordinates()`

**Current State:** 
Your existing `air_quality.py` works with city names but needs coordinate-based lookup.

**Implementation Steps:**

1. **Analyze Existing System:**
   ```python
   # Current air_quality.py probably does something like:
   def get_air_quality(city_name: str) -> Dict[str, str]:
       # Makes requests to Environment Canada
       pass
   ```

2. **Add Coordinate Lookup:**
   ```python
   def fetch_real_air_quality_by_coordinates(lat: float, lng: float) -> Dict[str, str]:
       # Option 1: Find nearest city
       nearest_city = find_nearest_city(lat, lng)
       return get_air_quality(nearest_city)
       
       # Option 2: Find nearest monitoring station
       nearest_station = find_nearest_air_quality_station(lat, lng)
       return get_station_air_quality(nearest_station)
       
       # Option 3: Use coordinate-based API if available
       return get_air_quality_coordinates(lat, lng)
   ```

3. **City/Station Database:**
   Create a database of cities/stations with coordinates:
   ```python
   CANADIAN_CITIES = [
       {"name": "Toronto", "lat": 43.6532, "lng": -79.3832},
       {"name": "Vancouver", "lat": 49.2827, "lng": -123.1207},
       # ... more cities
   ]
   
   def find_nearest_city(lat: float, lng: float) -> str:
       min_distance = float('inf')
       nearest_city = None
       
       for city in CANADIAN_CITIES:
           distance = calculate_distance(lat, lng, city["lat"], city["lng"])
           if distance < min_distance:
               min_distance = distance
               nearest_city = city["name"]
       
       return nearest_city
   ```

### 5. Spatial Database Integration

**Function:** `fetch_real_nearby_hotspots()`

**Options:**
- **PostGIS** (PostgreSQL with spatial extensions)
- **SQLite with SpatiaLite**
- **MongoDB with geospatial queries**

**Recommended: PostGIS for production**

1. **Database Setup:**
   ```sql
   CREATE TABLE hotspots (
       id SERIAL PRIMARY KEY,
       latitude DOUBLE PRECISION,
       longitude DOUBLE PRECISION,
       location GEOMETRY(POINT, 4326),
       confidence VARCHAR(20),
       brightness DOUBLE PRECISION,
       acquisition_date DATE,
       acquisition_time TIME,
       source VARCHAR(50)
   );
   
   CREATE INDEX idx_hotspots_location ON hotspots USING GIST(location);
   ```

2. **Implementation:**
   ```python
   import asyncpg
   
   async def fetch_real_nearby_hotspots(lat: float, lng: float, radius: int, limit: int = 100) -> Dict[str, Any]:
       conn = await asyncpg.connect(config.DATABASE_URL)
       
       query = """
       SELECT id, latitude, longitude, confidence, brightness,
              acquisition_date, acquisition_time,
              ST_Distance(location, ST_SetSRID(ST_Point($2, $1), 4326)) as distance
       FROM hotspots 
       WHERE ST_DWithin(location, ST_SetSRID(ST_Point($2, $1), 4326), $3)
       ORDER BY distance
       LIMIT $4
       """
       
       rows = await conn.fetch(query, lat, lng, radius, limit)
       
       hotspots = []
       for row in rows:
           hotspots.append({
               "id": row["id"],
               "latitude": row["latitude"], 
               "longitude": row["longitude"],
               "confidence": row["confidence"],
               "brightness": row["brightness"],
               "distance_meters": row["distance"]
           })
       
       await conn.close()
       
       return {
           "center": {"lat": lat, "lng": lng},
           "radius_meters": radius,
           "hotspots": hotspots,
           "total_found": len(hotspots)
       }
   ```

### 6. Caching Implementation

**Purpose:** Reduce API calls and improve performance

**Implementation:**

1. **Simple In-Memory Cache:**
   ```python
   from typing import Optional, Any
   from datetime import datetime
   
   class APICache:
       def __init__(self, ttl_seconds: int = 300):
           self._cache = {}
           self._ttl = ttl_seconds
       
       def get(self, key: str) -> Optional[Any]:
           if key in self._cache:
               data, timestamp = self._cache[key]
               if (datetime.now() - timestamp).total_seconds() < self._ttl:
                   return data
               del self._cache[key]
           return None
       
       def set(self, key: str, value: Any) -> None:
           self._cache[key] = (value, datetime.now())
   ```

2. **Usage in Functions:**
   ```python
   cache = APICache(ttl_seconds=300)  # 5 minutes
   
   async def cached_fetch_hotspots(bbox: Optional[str] = None) -> Dict[str, Any]:
       cache_key = f"hotspots_{bbox or 'global'}"
       
       # Try cache first
       cached = cache.get(cache_key)
       if cached:
           cached["cache_hit"] = True
           return cached
       
       # Fetch from API
       result = await fetch_real_hotspots(bbox)
       cache.set(cache_key, result)
       result["cache_hit"] = False
       
       return result
   ```

3. **Production Cache Options:**
   - **Redis** for distributed caching
   - **Memcached** for simple key-value caching
   - **Database caching** for persistence

## Integration with Server Endpoints

### Update server.py to use real data:

**Before:**
```python
@app.get("/api/orange/hotspots")
async def get_hotspots(bbox: Optional[str] = None):
    # Mock data
    return {"hotspots": [], "source": "mock"}
```

**After:**
```python
@app.get("/api/orange/hotspots")
async def get_hotspots(bbox: Optional[str] = None):
    from .data_sources import fetch_real_hotspots
    
    result = await fetch_real_hotspots(bbox=bbox)
    return result
```

## Error Handling Best Practices

1. **Always have fallbacks:**
   ```python
   try:
       result = await fetch_external_api()
   except Exception as e:
       logger.error(f"External API failed: {e}")
       result = get_mock_data()  # Fallback to mock
   ```

2. **Implement retries:**
   ```python
   for attempt in range(3):
       try:
           return await api_call()
       except aiohttp.ClientError:
           if attempt == 2:
               raise
           await asyncio.sleep(2 ** attempt)
   ```

3. **Log all external calls:**
   ```python
   logger.info(f"Calling external API: {url}")
   start_time = time.time()
   
   result = await api_call()
   
   duration = time.time() - start_time
   logger.info(f"API call completed in {duration:.2f}s")
   ```

## Testing Your Implementation

1. **Unit Tests:**
   ```python
   import pytest
   
   @pytest.mark.asyncio
   async def test_real_hotspots():
       result = await fetch_real_hotspots(bbox="-80,43,-79,44")
       assert "hotspots" in result
       assert result["source"] in ["NASA_FIRMS", "MOCK", "MOCK_FALLBACK"]
   ```

2. **Integration Tests:**
   ```python
   @pytest.mark.asyncio
   async def test_server_endpoint():
       from fastapi.testclient import TestClient
       
       response = client.get("/api/orange/hotspots?bbox=-80,43,-79,44")
       assert response.status_code == 200
       data = response.json()
       assert "hotspots" in data
   ```

3. **Load Testing:**
   ```bash
   # Test with multiple concurrent requests
   curl -s "http://localhost:8001/api/orange/hotspots" &
   curl -s "http://localhost:8001/api/orange/hotspots" &
   curl -s "http://localhost:8001/api/orange/hotspots" &
   wait
   ```

## Performance Optimization

1. **Use connection pooling:**
   ```python
   # Create session once, reuse for multiple requests
   session = aiohttp.ClientSession(
       connector=aiohttp.TCPConnector(limit=100),
       timeout=aiohttp.ClientTimeout(total=30)
   )
   ```

2. **Implement request batching:**
   ```python
   # Batch multiple requests together
   async def fetch_multiple_locations(locations: List[Tuple[float, float]]):
       tasks = [fetch_weather(lat, lng) for lat, lng in locations]
       results = await asyncio.gather(*tasks)
       return results
   ```

3. **Use async database connections:**
   ```python
   # Use async database drivers
   import asyncpg  # for PostgreSQL
   import aiomysql  # for MySQL
   import aiosqlite  # for SQLite
   ```

## Monitoring and Maintenance

1. **Add health checks:**
   ```python
   async def check_external_services():
       services = {}
       
       # Check NASA FIRMS
       try:
           await test_nasa_firms_api()
           services["nasa_firms"] = True
       except:
           services["nasa_firms"] = False
       
       return services
   ```

2. **Monitor API quotas:**
   ```python
   class APIQuotaMonitor:
       def __init__(self):
           self.request_counts = {}
       
       def record_request(self, service: str):
           hour = datetime.now().hour
           key = f"{service}_{hour}"
           self.request_counts[key] = self.request_counts.get(key, 0) + 1
       
       def check_quota(self, service: str, limit: int) -> bool:
           hour = datetime.now().hour
           key = f"{service}_{hour}"
           return self.request_counts.get(key, 0) < limit
   ```

3. **Set up alerts:**
   ```python
   if api_failure_rate > 0.1:  # More than 10% failures
       send_alert("High API failure rate detected")
   ```

## Next Steps

1. Start with NASA FIRMS integration (highest impact)
2. Add weather API integration  
3. Implement FWI calculations
4. Add caching and error handling
5. Set up monitoring and alerting
6. Optimize performance based on usage patterns

Remember to always test with small datasets first, implement proper error handling, and have fallback mechanisms to ensure your API remains functional even when external services are unavailable. 