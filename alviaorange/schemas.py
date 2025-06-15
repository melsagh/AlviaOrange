from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

# ============================================================================
# ENUMS
# ============================================================================

class HotspotSource(str, Enum):
    FIRMS = "FIRMS"
    VIIRS = "VIIRS"
    MODIS = "MODIS"
    GFW = "GFW"
    MANUAL = "manual"

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"

class DrynessLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"

class FuelModel(str, Enum):
    # Anderson 13 Fire Behavior Fuel Models
    GR1 = "GR1"  # Short, sparse dry climate grass
    GR2 = "GR2"  # Low load, dry climate grass
    GS1 = "GS1"  # Low load, dry climate grass-shrub
    GS2 = "GS2"  # Moderate load, dry climate grass-shrub
    SH1 = "SH1"  # Low load dry climate shrub
    SH2 = "SH2"  # Moderate load dry climate shrub
    TU1 = "TU1"  # Low load dry climate timber-understory
    TL1 = "TL1"  # Low load broadleaf litter
    # Add more as needed

class AlertType(str, Enum):
    HOTSPOT_DETECTED = "hotspot_detected"
    RISK_LEVEL_CHANGE = "risk_level_change"
    EXTREME_WEATHER = "extreme_weather"
    CRITICAL_FUEL_MOISTURE = "critical_fuel_moisture"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ============================================================================
# CORE DATA MODELS
# ============================================================================

class ZoneBounds(BaseModel):
    """Geographical bounds for a zone."""
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)
    
    @validator('north')
    def north_must_be_greater_than_south(cls, v, values):
        if 'south' in values and v <= values['south']:
            raise ValueError('north must be greater than south')
        return v

class Coordinates(BaseModel):
    """Simple latitude/longitude coordinates."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class TimeRange(BaseModel):
    """Time range for data queries."""
    start_date: datetime
    end_date: datetime
    
    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

# ============================================================================
# HOTSPOT MODELS
# ============================================================================

class HotspotMetadata(BaseModel):
    """Additional metadata for hotspot detections."""
    satellite: Optional[str] = None
    scan_angle: Optional[float] = None
    pixel_size: Optional[int] = None
    brightness_temp: Optional[float] = None

class Hotspot(BaseModel):
    """Represents a single wildfire hotspot detection."""
    id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timestamp: datetime
    confidence: Optional[int] = Field(None, ge=0, le=100)
    frp: Optional[float] = Field(None, description="Fire Radiative Power in MW")
    source: HotspotSource
    metadata: Optional[HotspotMetadata] = None

    class Config:
        orm_mode = True
        use_enum_values = True

class HotspotQueryResult(BaseModel):
    """Result of a hotspot query."""
    hotspots: List[Hotspot]
    total_count: int
    query_time: datetime

# ============================================================================
# WEATHER MODELS
# ============================================================================

class FireWeatherIndex(BaseModel):
    """Fire Weather Index components."""
    ffmc: float = Field(..., description="Fine Fuel Moisture Code")
    dmc: float = Field(..., description="Duff Moisture Code")
    dc: float = Field(..., description="Drought Code")
    isi: float = Field(..., description="Initial Spread Index")
    bui: float = Field(..., description="Buildup Index")
    fwi: float = Field(..., description="Fire Weather Index")

class WeatherData(BaseModel):
    """Current weather data relevant to fire risk."""
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity %")
    wind_speed: float = Field(..., ge=0, description="Wind speed in km/h")
    wind_direction: float = Field(..., ge=0, le=360, description="Wind direction in degrees")
    precipitation: float = Field(..., ge=0, description="Precipitation in mm")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure in hPa")
    visibility: Optional[float] = Field(None, description="Visibility in km")
    fire_weather_index: Optional[FireWeatherIndex] = None
    timestamp: datetime

class WeatherForecast(BaseModel):
    """Weather forecast data."""
    date: datetime
    temperature_max: float
    temperature_min: float
    humidity: float
    wind_speed: float
    wind_direction: float
    precipitation_probability: float = Field(..., ge=0, le=100)
    precipitation_amount: float = Field(..., ge=0)

# ============================================================================
# RISK ASSESSMENT MODELS
# ============================================================================

class ZoneData(BaseModel):
    """Zone-specific data for risk assessment."""
    bounds: ZoneBounds
    area_km2: float = Field(..., gt=0)

class VegetationData(BaseModel):
    """Vegetation data for risk assessment."""
    ndvi: Optional[float] = Field(None, ge=-1, le=1, description="Normalized Difference Vegetation Index")
    moisture_content: Optional[float] = Field(None, ge=0, le=100, description="Vegetation moisture %")
    fuel_load: Optional[float] = Field(None, ge=0, description="Fuel load in tons/hectare")

class TopographyData(BaseModel):
    """Topography data for risk assessment."""
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    slope: Optional[float] = Field(None, ge=0, le=90, description="Slope in degrees")
    aspect: Optional[float] = Field(None, ge=0, le=360, description="Aspect in degrees")

class RiskFactors(BaseModel):
    """Detailed risk factors breakdown."""
    temperature_factor: float = Field(..., ge=0, le=1)
    humidity_factor: float = Field(..., ge=0, le=1)
    wind_factor: float = Field(..., ge=0, le=1)
    fuel_moisture_factor: float = Field(..., ge=0, le=1)
    drought_index: float = Field(..., ge=0, le=1)
    slope_factor: Optional[float] = Field(None, ge=0, le=1)

class RiskAssessment(BaseModel):
    """Fire risk assessment result."""
    id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    timestamp: datetime
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    weather_risk: RiskLevel
    vegetation_dryness: DrynessLevel
    factors: RiskFactors
    recommendations: List[str] = []

    class Config:
        orm_mode = True
        use_enum_values = True

# ============================================================================
# FIRE BEHAVIOR MODELS
# ============================================================================

class FireSpreadPolygon(BaseModel):
    """Fire spread polygon for a specific time."""
    time_hours: int = Field(..., ge=0)
    perimeter: List[Coordinates]
    area_hectares: float = Field(..., ge=0)

class FireSpreadPrediction(BaseModel):
    """Fire spread prediction result."""
    spread_polygons: List[FireSpreadPolygon]
    max_spread_rate: float = Field(..., ge=0, description="Maximum spread rate in m/min")
    flame_length: float = Field(..., ge=0, description="Flame length in meters")
    fire_intensity: float = Field(..., ge=0, description="Fire intensity in kW/m")
    model_used: str
    confidence: float = Field(..., ge=0, le=1)

# ============================================================================
# FUEL ANALYSIS MODELS
# ============================================================================

class FuelAnalysis(BaseModel):
    """Fuel load analysis result."""
    fuel_load_tons_per_hectare: float = Field(..., ge=0)
    fuel_type: str
    fuel_model: FuelModel
    live_fuel_moisture: float = Field(..., ge=0, le=100)
    dead_fuel_moisture: float = Field(..., ge=0, le=100)
    analysis_date: datetime
    confidence: float = Field(..., ge=0, le=1)
    data_source: str

    class Config:
        use_enum_values = True

# ============================================================================
# ALERT SYSTEM MODELS
# ============================================================================

class AlertData(BaseModel):
    """Alert-specific data."""
    hotspot_count: Optional[int] = None
    max_confidence: Optional[int] = None
    risk_score: Optional[int] = None

class Alert(BaseModel):
    """Fire alert notification."""
    alert_id: UUID
    zone_id: UUID
    alert_type: AlertType
    severity: AlertSeverity
    timestamp: datetime
    data: AlertData
    actions_required: List[str] = []

    class Config:
        use_enum_values = True

# ============================================================================
# API RESPONSE MODELS
# ============================================================================

class APIResponse(BaseModel):
    """Base API response model."""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(APIResponse):
    """Error response model."""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None 