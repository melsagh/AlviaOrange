"""
Configuration settings for AlviaOrange external data sources.

This module manages API keys, endpoints, and settings for external services.
Set environment variables to configure real data sources.
"""

import os
from typing import Dict, Any, Optional

# ============================================================================
# EXTERNAL API CONFIGURATION
# ============================================================================

class DataSourceConfig:
    """Configuration for external data sources."""
    
    # NASA FIRMS (Fire Information for Resource Management System)
    NASA_FIRMS_API_KEY = os.getenv("NASA_FIRMS_API_KEY", "demo_key")
    NASA_FIRMS_BASE_URL = "https://nrt3.modaps.eosdis.nasa.gov/api/v2/content/archives/FIRMS"
    
    # Environment Canada
    ENVIRONMENT_CANADA_BASE_URL = "https://dd.weather.gc.ca"
    ENVIRONMENT_CANADA_TIMEOUT = int(os.getenv("ENVIRONMENT_CANADA_TIMEOUT", "30"))
    
    # Canadian Wildland Fire Information System (CWFIS)
    CWFIS_BASE_URL = "https://cwfis.cfs.nrcan.gc.ca"
    CWFIS_TIMEOUT = int(os.getenv("CWFIS_TIMEOUT", "30"))
    
    # OpenWeatherMap (alternative weather source)
    OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
    OPENWEATHERMAP_BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    # NOAA (National Oceanic and Atmospheric Administration)
    NOAA_API_KEY = os.getenv("NOAA_API_KEY", "")
    NOAA_BASE_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2"
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "1000"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))
    
    # Cache settings
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 minutes
    CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    
    # Database settings (for storing processed data)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///alviaorange.db")
    
    # Geospatial settings
    DEFAULT_SPATIAL_REFERENCE = "EPSG:4326"
    MAX_BBOX_SIZE_DEGREES = float(os.getenv("MAX_BBOX_SIZE_DEGREES", "10.0"))
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """
        Validate configuration and return status of external services.
        
        Returns:
            Dict mapping service names to availability status
        """
        services = {
            "nasa_firms": bool(cls.NASA_FIRMS_API_KEY and cls.NASA_FIRMS_API_KEY != "demo_key"),
            "openweathermap": bool(cls.OPENWEATHERMAP_API_KEY),
            "noaa": bool(cls.NOAA_API_KEY),
            "environment_canada": True,  # No API key required for public data
            "cwfis": True,  # No API key required for public data
        }
        return services
    
    @classmethod
    def get_api_endpoints(cls) -> Dict[str, str]:
        """
        Get all configured API endpoints.
        
        Returns:
            Dict mapping service names to base URLs
        """
        return {
            "nasa_firms": cls.NASA_FIRMS_BASE_URL,
            "environment_canada": cls.ENVIRONMENT_CANADA_BASE_URL,
            "cwfis": cls.CWFIS_BASE_URL,
            "openweathermap": cls.OPENWEATHERMAP_BASE_URL,
            "noaa": cls.NOAA_BASE_URL,
        }

# ============================================================================
# FIRE WEATHER INDEX CONFIGURATION
# ============================================================================

class FWIConfig:
    """Configuration for Fire Weather Index calculations."""
    
    # FWI System parameters
    FWI_PARAMS = {
        "ffmc_default": 85.0,  # Fine Fuel Moisture Code default
        "dmc_default": 6.0,    # Duff Moisture Code default  
        "dc_default": 15.0,    # Drought Code default
        "snow_depth_threshold": 1.0,  # cm, below which snow is ignored
        "rain_threshold": 0.5,  # mm, minimum rain for moisture calculation
    }
    
    # Danger classes
    DANGER_CLASSES = {
        (0, 2): "Very Low",
        (2, 4): "Low", 
        (4, 8): "Moderate",
        (8, 16): "High",
        (16, 30): "Very High",
        (30, float('inf')): "Extreme"
    }
    
    @classmethod
    def get_danger_class(cls, fwi_value: float) -> str:
        """Get danger class for FWI value."""
        for (low, high), danger_class in cls.DANGER_CLASSES.items():
            if low <= fwi_value < high:
                return danger_class
        return "Extreme"

# ============================================================================
# SPATIAL CONFIGURATION
# ============================================================================

class SpatialConfig:
    """Configuration for spatial operations."""
    
    # Coordinate system settings
    WGS84_EPSG = 4326
    WEB_MERCATOR_EPSG = 3857
    
    # Default spatial query limits
    MAX_HOTSPOTS_PER_QUERY = int(os.getenv("MAX_HOTSPOTS_PER_QUERY", "10000"))
    MAX_RADIUS_METERS = int(os.getenv("MAX_RADIUS_METERS", "500000"))  # 500km
    DEFAULT_RADIUS_METERS = int(os.getenv("DEFAULT_RADIUS_METERS", "50000"))  # 50km
    
    # Tile service settings
    TILE_SIZE = 256
    MIN_ZOOM = 0
    MAX_ZOOM = 18
    
    # Bounding box validation
    MIN_LAT = -90.0
    MAX_LAT = 90.0
    MIN_LNG = -180.0
    MAX_LNG = 180.0

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class LoggingConfig:
    """Configuration for logging external API calls."""
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Enable/disable logging for different services
    LOG_API_CALLS = os.getenv("LOG_API_CALLS", "true").lower() == "true"
    LOG_RESPONSE_TIMES = os.getenv("LOG_RESPONSE_TIMES", "true").lower() == "true"
    LOG_CACHE_HITS = os.getenv("LOG_CACHE_HITS", "false").lower() == "true"

# ============================================================================
# DEVELOPMENT/TESTING CONFIGURATION
# ============================================================================

class DevelopmentConfig:
    """Configuration for development and testing."""
    
    # Mock data settings
    USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
    MOCK_DELAY_SECONDS = float(os.getenv("MOCK_DELAY_SECONDS", "0.1"))
    
    # Testing settings  
    ENABLE_DEBUG_ENDPOINTS = os.getenv("ENABLE_DEBUG_ENDPOINTS", "false").lower() == "true"
    SKIP_EXTERNAL_APIS = os.getenv("SKIP_EXTERNAL_APIS", "false").lower() == "true"
    
    # Sample data paths
    SAMPLE_DATA_DIR = os.getenv("SAMPLE_DATA_DIR", "data/samples")

# Create global config instance
config = DataSourceConfig()
fwi_config = FWIConfig()
spatial_config = SpatialConfig()
logging_config = LoggingConfig()
dev_config = DevelopmentConfig() 