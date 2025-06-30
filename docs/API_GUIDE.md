# AlviaOrange API v2.1.0 - Complete Guide

The AlviaOrange API provides comprehensive wildfire monitoring and risk assessment capabilities. This guide covers all available endpoints, authentication, and usage examples.

## 🚀 Quick Start

### 1. Start the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python scripts/run_server.py
```

The server will start on `http://localhost:8001` by default.

### 2. Authentication

All API endpoints require authentication via API key in the header:

```bash
curl -H "X-API-Key: demo-key" http://localhost:8001/api/orange/health
```

**Default API Keys for Development:**
- `demo-key`
- `test-key` 
- `development-key`

**Production Setup:**
Set the `VALID_API_KEYS` environment variable:
```bash
export VALID_API_KEYS="your-production-key-1,your-production-key-2"
```

### 3. Interactive Documentation

Visit `http://localhost:8001/api/orange/docs` for interactive API documentation powered by Swagger UI.

## 📍 Endpoints Overview

### System Health
- `GET /api/orange/health` - System health check

### Hotspot Detection
- `GET /api/orange/hotspots` - General hotspot detection with spatial support
- `GET /api/orange/hotspots/active` - Active hotspots with geographic bounds
- `GET /api/orange/hotspots/near` - Find hotspots near coordinates

### Air Quality
- `GET /api/orange/air-quality` - Basic air quality data
- `GET /api/orange/air-quality/scale` - Air quality scale definitions  
- `GET /api/orange/air-quality/history` - Historical air quality data

### Weather Services
- `GET /api/orange/weather/forecast` - Weather forecast for location
- `GET /api/orange/weather/current` - Current weather conditions
- `GET /api/orange/weather/fire-index` - Fire weather index

### Fire Danger Assessment
- `GET /api/orange/fire-danger/risk` - Fire danger risk assessment
- `GET /api/orange/fire-danger/rating` - Fire danger rating grid

### Climate Data
- `GET /api/orange/climate/stations` - Climate stations in area
- `GET /api/orange/climate/normals` - Climate normals for station

### Geospatial Services
- `GET /api/orange/wms/tiles/{z}/{x}/{y}` - WMS tile service
- `GET /api/orange/geospatial/capabilities` - Geospatial service capabilities

### Zone-Specific Services
- `GET /api/orange/zones/{zone_id}/risk-assessment` - Zone risk assessment
- `GET /api/orange/zones/{zone_id}/monitoring` - Zone monitoring status

## 🔥 Detailed Endpoint Documentation

### System Health

#### GET /api/orange/health

Check system health and service availability.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00Z",
  "version": "2.1.0",
  "database_connected": true,
  "external_services": {
    "environment_canada": true,
    "cwfis": true,
    "nasa_firms": true
  }
}
```

---

### Hotspot Detection

#### GET /api/orange/hotspots

Enhanced hotspot detection with spatial support.

**Parameters:**
- `bbox` (optional): Bounding box as `lng_min,lat_min,lng_max,lat_max`

**Examples:**

```bash
# Get hotspots within bounding box
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/hotspots?bbox=-80.0,43.0,-79.0,44.0"

# Get general hotspots (fallback behavior)
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/hotspots"
```

**Response:**
```json
{
  "hotspots": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "latitude": 43.2567,
      "longitude": -79.4521,
      "timestamp": "2024-01-20T15:30:00Z",
      "confidence": 85,
      "frp": 12.5,
      "source": "VIIRS",
      "metadata": {
        "satellite": "NOAA-20",
        "scan_angle": 15.2,
        "pixel_size": 375,
        "brightness_temp": 320.5
      }
    }
  ],
  "bbox": {
    "sw": {"lat": 43.0, "lng": -80.0},
    "ne": {"lat": 44.0, "lng": -79.0}
  },
  "spatial_reference": "EPSG:4326",
  "total_count": 1
}
```

#### GET /api/orange/hotspots/active

Get currently active hotspots with enhanced spatial support.

**Parameters:**
- `zone_id` (optional): Specific zone UUID
- `bbox` (optional): Bounding box filter
- `hours_back` (optional): Hours to look back (default: 24, max: 168)

**Examples:**

```bash
# Get active hotspots by zone
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/hotspots/active?zone_id=8f1d823d-4258-4789-902d-1208ebc8bbb7"

# Get active hotspots in bounding box
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/hotspots/active?bbox=-80.0,43.0,-79.0,44.0&hours_back=48"
```

**Response (Zone-based):**
```json
{
  "zone_id": "8f1d823d-4258-4789-902d-1208ebc8bbb7",
  "zone_boundary": "POLYGON((-80 43, -79 43, -79 44, -80 44, -80 43))",
  "hotspots_in_zone": 12,
  "hotspots": [
    {
      "id": "MODIS_67890",
      "lat": 43.7234,
      "lng": -79.1234,
      "distance_from_center_km": 2.3,
      "within_zone": true
    }
  ]
}
```

#### GET /api/orange/hotspots/near

Find hotspots within radius of specific coordinates.

**Parameters:**
- `lat` (required): Latitude (-90 to 90)
- `lng` (required): Longitude (-180 to 180)
- `radius` (optional): Search radius in meters (default: 50000, max: 500000)
- `limit` (optional): Maximum results (default: 100, max: 1000)

**Example:**

```bash
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/hotspots/near?lat=43.6532&lng=-79.3832&radius=25000&limit=50"
```

**Response:**
```json
{
  "hotspots": [
    {
      "id": "MODIS_12345",
      "latitude": 43.6234,
      "longitude": -79.3567,
      "timestamp": "2024-01-20T14:30:00Z",
      "confidence": 92,
      "distance_km": 15.2
    }
  ],
  "search_center": {"lat": 43.6532, "lng": -79.3832},
  "search_radius_km": 25.0,
  "total_count": 1
}
```

---

### Air Quality

#### GET /api/orange/air-quality/scale

Get air quality scale definitions with color coding.

**Example:**

```bash
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/air-quality/scale"
```

**Response:**
```json
{
  "scales": [
    {
      "name": "AQI",
      "ranges": [
        {"min": 0, "max": 50, "level": "Good", "color": "#00e400"},
        {"min": 51, "max": 100, "level": "Moderate", "color": "#ffff00"},
        {"min": 101, "max": 150, "level": "Unhealthy for Sensitive Groups", "color": "#ff7e00"},
        {"min": 151, "max": 200, "level": "Unhealthy", "color": "#ff0000"},
        {"min": 201, "max": 300, "level": "Very Unhealthy", "color": "#8f3f97"},
        {"min": 301, "max": 500, "level": "Hazardous", "color": "#7e0023"}
      ]
    }
  ]
}
```

#### GET /api/orange/air-quality/history

Get historical air quality data for specific coordinates.

**Parameters:**
- `lat` (required): Latitude
- `lng` (required): Longitude  
- `start` (required): Start date in ISO 8601 format
- `end` (required): End date in ISO 8601 format

**Example:**

```bash
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/air-quality/history?lat=43.6532&lng=-79.3832&start=2024-01-01T00:00:00Z&end=2024-01-31T23:59:59Z"
```

**Response:**
```json
{
  "location": {
    "lat": 43.6532,
    "lng": -79.3832,
    "name": "Toronto"
  },
  "measurements": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "aqi": 45,
      "pm25": 12.5,
      "pm10": 18.2,
      "o3": 28.1,
      "no2": 15.3,
      "so2": 2.1,
      "co": 0.8
    }
  ]
}
```

---

### Weather Services

#### GET /api/orange/weather/forecast

Get weather forecast for specific location.

**Parameters:**
- `lat` (required): Latitude
- `lng` (required): Longitude
- `days` (optional): Number of forecast days (default: 7, max: 14)

**Example:**

```bash
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/weather/forecast?lat=43.6532&lng=-79.3832&days=7"
```

**Response:**
```json
{
  "location": {"lat": 43.6532, "lng": -79.3832},
  "forecast": [
    {
      "date": "2024-01-20",
      "temp_max": 5,
      "temp_min": -2,
      "humidity": 65,
      "wind_speed": 15,
      "wind_direction": 220,
      "precipitation": 2.5,
      "conditions": "Snow"
    }
  ]
}
```

#### GET /api/orange/weather/fire-index

Get fire weather index for location.

**Parameters:**
- `lat` (required): Latitude
- `lng` (required): Longitude

**Example:**

```bash
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/weather/fire-index?lat=43.6532&lng=-79.3832"
```

**Response:**
```json
{
  "location": {"lat": 43.6532, "lng": -79.3832},
  "fire_weather": {
    "timestamp": "2024-01-20T10:30:00Z",
    "fwi": 8.5,
    "ffmc": 85.2,
    "dmc": 15.8,
    "dc": 125.4,
    "isi": 3.2,
    "bui": 18.7,
    "danger_class": "Moderate",
    "risk_level": "Medium"
  }
}
```

---

### Fire Danger Assessment

#### GET /api/orange/fire-danger/risk

Get comprehensive fire danger risk assessment for an area.

**Parameters:**
- `lat` (required): Center latitude
- `lng` (required): Center longitude
- `radius` (optional): Analysis radius in meters (default: 50000, max: 200000)

**Example:**

```bash
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/fire-danger/risk?lat=43.6532&lng=-79.3832&radius=50000"
```

**Response:**
```json
{
  "center": {"lat": 43.6532, "lng": -79.3832},
  "radius_meters": 50000,
  "risk_assessment": {
    "overall_risk": "High",
    "fire_weather_index": 12.8,
    "drought_code": 245.6,
    "fuel_moisture": 8.2,
    "historical_incidents": 23,
    "seasonal_factor": 1.4,
    "risk_factors": [
      "Low humidity",
      "High wind speed",
      "Dry vegetation"
    ]
  }
}
```

#### GET /api/orange/fire-danger/rating

Get fire danger rating grid for a bounded area.

**Parameters:**
- `bbox` (required): Bounding box as `lng_min,lat_min,lng_max,lat_max`
- `resolution` (optional): Grid resolution in meters (default: 1000, max: 10000)

**Example:**

```bash
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/fire-danger/rating?bbox=-80.0,43.0,-79.0,44.0&resolution=1000"
```

**Response:**
```json
{
  "bbox": {
    "sw": {"lat": 43.0, "lng": -80.0},
    "ne": {"lat": 44.0, "lng": -79.0}
  },
  "resolution_meters": 1000,
  "grid_data": [
    {
      "lat": 43.0,
      "lng": -80.0,
      "danger_rating": "Low",
      "fwi": 4.2
    },
    {
      "lat": 43.0,
      "lng": -79.9,
      "danger_rating": "Moderate",
      "fwi": 7.8
    }
  ]
}
```

---

### Zone-Specific Services

#### GET /api/orange/zones/{zone_id}/risk-assessment

Get comprehensive risk assessment for a specific zone.

**Parameters:**
- `zone_id` (required): Zone UUID

**Example:**

```bash
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/zones/8f1d823d-4258-4789-902d-1208ebc8bbb7/risk-assessment"
```

**Response:**
```json
{
  "zone_id": "8f1d823d-4258-4789-902d-1208ebc8bbb7",
  "zone_name": "Algonquin Provincial Park",
  "area_km2": 7653.45,
  "risk_assessment": {
    "overall_risk": "High",
    "fire_weather_index": 15.2,
    "active_hotspots": 8,
    "weather_conditions": {
      "temperature": 28,
      "humidity": 35,
      "wind_speed": 25
    },
    "vegetation_dryness": "Extreme",
    "historical_fire_frequency": "Medium",
    "evacuation_routes": 3,
    "populated_areas_at_risk": ["Huntsville", "Dwight"]
  }
}
```

#### GET /api/orange/zones/{zone_id}/monitoring

Get monitoring status for a specific zone.

**Example:**

```bash
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/zones/8f1d823d-4258-4789-902d-1208ebc8bbb7/monitoring"
```

**Response:**
```json
{
  "zone_id": "8f1d823d-4258-4789-902d-1208ebc8bbb7",
  "monitoring_status": {
    "active_sensors": 15,
    "last_update": "2024-01-20T16:45:00Z",
    "coverage_percentage": 87.5,
    "sensor_types": ["temperature", "humidity", "smoke", "camera"],
    "alerts_last_24h": 3
  }
}
```

---

## 🌍 Geospatial Services

### WMS Tiles

#### GET /api/orange/wms/tiles/{z}/{x}/{y}

Get WMS tiles for geospatial layers.

**Parameters:**
- `z` (required): Zoom level (0-18)
- `x` (required): Tile X coordinate
- `y` (required): Tile Y coordinate
- `layer` (optional): Layer name (default: "fire-danger")
- `style` (optional): Style name (default: "default")

**Example:**

```bash
curl -H "X-API-Key: demo-key" -o tile.png \
  "http://localhost:8001/api/orange/wms/tiles/10/256/384?layer=fire-danger&style=default"
```

**Response:** Binary PNG tile data

### Capabilities

#### GET /api/orange/geospatial/capabilities

Get available geospatial layers and their capabilities.

**Example:**

```bash
curl -H "X-API-Key: demo-key" \
  "http://localhost:8001/api/orange/geospatial/capabilities"
```

**Response:**
```json
{
  "layers": [
    {
      "name": "fire-danger",
      "title": "Fire Danger Rating",
      "bbox": {
        "sw": {"lat": 41.0, "lng": -141.0},
        "ne": {"lat": 84.0, "lng": -52.0}
      },
      "zoom_levels": {"min": 1, "max": 12},
      "styles": ["default", "grayscale"]
    }
  ]
}
```

---

## 🚨 Error Handling

All endpoints return consistent error responses:

```json
{
  "error": {
    "code": "HTTP_400",
    "message": "Invalid coordinates provided",
    "details": {
      "provided_lat": 95.5
    }
  }
}
```

**Common Error Codes:**
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing/invalid API key)
- `404` - Not Found
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8001` | Server port |
| `HOST` | `0.0.0.0` | Server host |
| `VALID_API_KEYS` | `demo-key,test-key,development-key` | Comma-separated API keys |
| `RATE_LIMIT_REQUESTS` | `1000` | Requests per hour per API key |
| `RATE_LIMIT_WINDOW` | `3600` | Rate limit window in seconds |
| `NASA_FIRMS_API_KEY` | `demo_key` | NASA FIRMS API key |

### Production Deployment

```bash
# Set production environment variables
export VALID_API_KEYS="prod-key-1,prod-key-2"
export NASA_FIRMS_API_KEY="your-real-nasa-key"
export PORT=8001
export RELOAD=false

# Start server
python scripts/run_server.py
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PORT=8001
ENV HOST=0.0.0.0
ENV RELOAD=false

EXPOSE 8001

CMD ["python", "scripts/run_server.py"]
```

---

## 📊 Rate Limiting

- **Default Limit:** 1000 requests per hour per API key
- **Rate Limit Headers:** Included in all responses
- **Exceeded Limit:** Returns HTTP 429 with retry information

---

## 🔐 CORS Configuration

The API is configured to allow requests from:
- `https://alvia-platform.com` (production)
- `http://localhost:5173` (development frontend)
- `http://localhost:3000` (alternative dev port)

---

## 💡 Usage Tips

1. **Caching:** Responses include appropriate cache headers
2. **Pagination:** Large datasets are automatically limited
3. **Coordinates:** Always use WGS84 (EPSG:4326) format
4. **Dates:** Use ISO 8601 format with UTC timezone
5. **Bounding Boxes:** Format as `lng_min,lat_min,lng_max,lat_max`

---

## 🔄 Legacy Compatibility

The following legacy endpoints remain available:
- `GET /hotspots`
- `GET /air_quality` 
- `GET /air_quality/scale`
- `GET /air_quality/history`
- All `/cwfis/*` endpoints

---

## 📞 Support

For API support or questions:
- Check the interactive documentation at `/api/orange/docs`
- Review the health endpoint at `/api/orange/health`
- Consult the main project documentation

---

## 🎯 Next Steps

1. Start the server: `python scripts/run_server.py`
2. Test the health endpoint: `curl -H "X-API-Key: demo-key" http://localhost:8001/api/orange/health`
3. Explore the interactive docs: `http://localhost:8001/api/orange/docs`
4. Try the hotspot detection: `curl -H "X-API-Key: demo-key" "http://localhost:8001/api/orange/hotspots?bbox=-80.0,43.0,-79.0,44.0"`

The API is now ready for integration with your Alvia Platform! 