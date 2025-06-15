"""
Fire risk assessment module for calculating comprehensive fire risk scores.

This module provides functions to calculate fire risk based on multiple factors
including weather conditions, vegetation data, and topographical information.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from .schemas import (
    RiskAssessment, RiskLevel, DrynessLevel, RiskFactors,
    ZoneData, WeatherData, VegetationData, TopographyData,
    APIResponse, ErrorResponse
)

# Configure logging
logger = logging.getLogger(__name__)

class RiskAssessmentError(Exception):
    """Custom exception for risk assessment errors."""
    pass

def calculate_fire_risk_score(
    zone_data: Dict,
    weather_data: Dict,
    vegetation_data: Dict,
    topography_data: Optional[Dict] = None
) -> Dict:
    """
    Calculate comprehensive fire risk score using multiple factors.
    
    Args:
        zone_data: Zone information including bounds and area
        weather_data: Current weather conditions
        vegetation_data: Vegetation moisture and fuel load data
        topography_data: Optional topographical information
        
    Returns:
        Dictionary containing risk assessment results
        
    Raises:
        RiskAssessmentError: When risk calculation fails
        ValueError: When input parameters are invalid
    """
    try:
        # Validate and parse input data
        zone = ZoneData(**zone_data)
        weather = WeatherData(**weather_data)
        vegetation = VegetationData(**vegetation_data)
        topography = TopographyData(**topography_data) if topography_data else None
        
        # Calculate individual risk factors
        factors = _calculate_risk_factors(weather, vegetation, topography)
        
        # Calculate overall risk score (0-100)
        risk_score = _calculate_overall_risk_score(factors)
        
        # Determine risk level
        risk_level = _determine_risk_level(risk_score)
        
        # Determine weather-specific risk
        weather_risk = _determine_weather_risk(weather)
        
        # Determine vegetation dryness level
        vegetation_dryness = _determine_vegetation_dryness(vegetation)
        
        # Generate recommendations
        recommendations = _generate_recommendations(risk_score, factors, weather, vegetation)
        
        # Create risk assessment object
        assessment = RiskAssessment(
            id=uuid4(),
            timestamp=datetime.now(),
            risk_score=risk_score,
            risk_level=risk_level,
            weather_risk=weather_risk,
            vegetation_dryness=vegetation_dryness,
            factors=factors,
            recommendations=recommendations
        )
        
        return assessment.dict()
        
    except Exception as e:
        logger.error(f"Risk assessment calculation failed: {str(e)}")
        raise RiskAssessmentError(f"Failed to calculate fire risk: {str(e)}")

def _calculate_risk_factors(
    weather: WeatherData,
    vegetation: VegetationData,
    topography: Optional[TopographyData]
) -> RiskFactors:
    """
    Calculate individual risk factors from input data.
    
    Args:
        weather: Weather data
        vegetation: Vegetation data
        topography: Optional topography data
        
    Returns:
        RiskFactors object with calculated factor values
    """
    # Temperature factor (0-1, higher temperature = higher risk)
    # Risk increases significantly above 30°C
    temp_factor = min(1.0, max(0.0, (weather.temperature - 10) / 30))
    
    # Humidity factor (0-1, lower humidity = higher risk)
    # Risk is highest when humidity < 20%
    humidity_factor = max(0.0, min(1.0, (100 - weather.humidity) / 80))
    
    # Wind factor (0-1, higher wind speed = higher risk)
    # Risk increases significantly above 20 km/h
    wind_factor = min(1.0, max(0.0, weather.wind_speed / 50))
    
    # Fuel moisture factor (0-1, lower moisture = higher risk)
    if vegetation.moisture_content is not None:
        fuel_moisture_factor = max(0.0, min(1.0, (100 - vegetation.moisture_content) / 80))
    else:
        # Use humidity as proxy if vegetation moisture not available
        fuel_moisture_factor = humidity_factor
    
    # Drought index (simplified calculation based on precipitation and humidity)
    # In a real implementation, this would use standardized drought indices
    drought_index = min(1.0, max(0.0, (100 - weather.humidity) / 100))
    if weather.precipitation > 0:
        drought_index *= max(0.1, 1.0 - (weather.precipitation / 10))
    
    # Slope factor (optional, higher slope = higher risk)
    slope_factor = None
    if topography and topography.slope is not None:
        # Risk increases with slope, maxing out around 45 degrees
        slope_factor = min(1.0, max(0.0, topography.slope / 45))
    
    return RiskFactors(
        temperature_factor=temp_factor,
        humidity_factor=humidity_factor,
        wind_factor=wind_factor,
        fuel_moisture_factor=fuel_moisture_factor,
        drought_index=drought_index,
        slope_factor=slope_factor
    )

def _calculate_overall_risk_score(factors: RiskFactors) -> int:
    """
    Calculate overall risk score from individual factors.
    
    Args:
        factors: Individual risk factors
        
    Returns:
        Overall risk score (0-100)
    """
    # Weighted combination of factors
    weights = {
        'temperature': 0.2,
        'humidity': 0.25,
        'wind': 0.2,
        'fuel_moisture': 0.25,
        'drought': 0.1
    }
    
    score = (
        factors.temperature_factor * weights['temperature'] +
        factors.humidity_factor * weights['humidity'] +
        factors.wind_factor * weights['wind'] +
        factors.fuel_moisture_factor * weights['fuel_moisture'] +
        factors.drought_index * weights['drought']
    )
    
    # Add slope factor if available (bonus risk)
    if factors.slope_factor is not None:
        score += factors.slope_factor * 0.1
        score = min(1.0, score)  # Cap at 1.0
    
    # Convert to 0-100 scale
    return int(score * 100)

def _determine_risk_level(risk_score: int) -> RiskLevel:
    """
    Determine risk level category from numerical score.
    
    Args:
        risk_score: Numerical risk score (0-100)
        
    Returns:
        Risk level category
    """
    if risk_score >= 80:
        return RiskLevel.EXTREME
    elif risk_score >= 60:
        return RiskLevel.HIGH
    elif risk_score >= 30:
        return RiskLevel.MODERATE
    else:
        return RiskLevel.LOW

def _determine_weather_risk(weather: WeatherData) -> RiskLevel:
    """
    Determine weather-specific risk level.
    
    Args:
        weather: Weather data
        
    Returns:
        Weather risk level
    """
    # High temperature, low humidity, high wind = extreme weather risk
    temp_risk = weather.temperature > 35
    humidity_risk = weather.humidity < 15
    wind_risk = weather.wind_speed > 30
    
    risk_factors = sum([temp_risk, humidity_risk, wind_risk])
    
    if risk_factors >= 3:
        return RiskLevel.EXTREME
    elif risk_factors >= 2:
        return RiskLevel.HIGH
    elif risk_factors >= 1:
        return RiskLevel.MODERATE
    else:
        return RiskLevel.LOW

def _determine_vegetation_dryness(vegetation: VegetationData) -> DrynessLevel:
    """
    Determine vegetation dryness level.
    
    Args:
        vegetation: Vegetation data
        
    Returns:
        Vegetation dryness level
    """
    if vegetation.moisture_content is None:
        return DrynessLevel.MODERATE  # Default when data unavailable
    
    moisture = vegetation.moisture_content
    
    if moisture < 10:
        return DrynessLevel.SEVERE
    elif moisture < 20:
        return DrynessLevel.HIGH
    elif moisture < 40:
        return DrynessLevel.MODERATE
    else:
        return DrynessLevel.LOW

def _generate_recommendations(
    risk_score: int,
    factors: RiskFactors,
    weather: WeatherData,
    vegetation: VegetationData
) -> List[str]:
    """
    Generate actionable recommendations based on risk assessment.
    
    Args:
        risk_score: Overall risk score
        factors: Individual risk factors
        weather: Weather data
        vegetation: Vegetation data
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # High-level recommendations based on overall risk
    if risk_score >= 80:
        recommendations.extend([
            "EXTREME FIRE RISK - Implement immediate fire restrictions",
            "Deploy additional fire suppression resources",
            "Issue public fire danger warnings",
            "Consider evacuation planning for high-risk areas"
        ])
    elif risk_score >= 60:
        recommendations.extend([
            "HIGH FIRE RISK - Increase monitoring frequency",
            "Alert local fire departments",
            "Consider fire restrictions",
            "Monitor weather conditions closely"
        ])
    elif risk_score >= 30:
        recommendations.extend([
            "MODERATE FIRE RISK - Maintain standard monitoring",
            "Review fire suppression readiness"
        ])
    
    # Specific recommendations based on individual factors
    if factors.humidity_factor > 0.7:
        recommendations.append("Low humidity detected - increase fire patrol frequency")
    
    if factors.wind_factor > 0.6:
        recommendations.append("High wind conditions - monitor for rapid fire spread potential")
    
    if factors.temperature_factor > 0.8:
        recommendations.append("Extreme temperatures - consider heat-related fire restrictions")
    
    if factors.fuel_moisture_factor > 0.7:
        recommendations.append("Dry fuel conditions - prioritize fuel moisture monitoring")
    
    if weather.precipitation == 0 and factors.drought_index > 0.6:
        recommendations.append("Drought conditions present - monitor soil and vegetation moisture")
    
    return recommendations 