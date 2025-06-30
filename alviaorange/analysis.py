"""
Wildfire Analysis Primitives for the AlviaOrange Toolkit.

This module provides higher-level analytical functions for wildfire and
climate science applications, moving beyond simple data retrieval. These
primitives are designed to be composable and useful for both direct API
access and library-based scientific workflows.

Core Analytical Domains:
1. Drought & Moisture Analysis
2. Fire Season Severity & Anomaly Detection
3. Fire Behavior Prediction (Simplified)
4. Geospatial & Risk Analysis
"""

from __future__ import annotations
import pandas as pd
from typing import Dict, Any, Optional
import asyncio

from .weather_stations import get_station_weather_data
from .example_implementation import fetch_climate_normals_from_ec
from .fwi_calculator import calculate_fwi
from .config import fwi_config
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# 1. DROUGHT & MOISTURE ANALYSIS
# ============================================================================

def calculate_drought_index(
    station_id: str,
    year: int,
    month: int
) -> Dict[str, Any]:
    """
    Calculates a simplified drought index based on precipitation anomaly.

    This primitive compares the total precipitation for a given month against
    the long-term normal for that month. A value < 1.0 indicates drier than
    average conditions.

    Args:
        station_id: The climate station identifier.
        year: The year to analyze.
        month: The month to analyze (1-12).

    Returns:
        A dictionary containing the drought analysis.
    """
    try:
        # For now, use simplified mock normals since EC integration is complex
        # In production, this would fetch from Environment Canada
        mock_normals = {
            1: 50, 2: 45, 3: 60, 4: 70, 5: 80, 6: 90,
            7: 85, 8: 80, 9: 75, 10: 65, 11: 55, 12: 50
        }
        normal_precip = mock_normals.get(month, 60)

        # Step 2: Fetch the actual weather data for the specified month
        start_date = f"{year}-{month:02d}-01"
        end_date_obj = pd.to_datetime(start_date) + pd.offsets.MonthEnd(1)
        if pd.isna(end_date_obj):
            raise ValueError("Could not determine a valid end date.")
        end_date = end_date_obj.strftime('%Y-%m-%d')
        
        monthly_data_df = get_station_weather_data(
            station_id, start_date, end_date, data_type='daily'
        )

        if monthly_data_df.empty:
            raise Exception(f"No historical data found for {year}-{month}.")

        actual_precip = monthly_data_df['TOTAL_PRECIPITATION'].sum()

        # Step 3: Calculate the drought index (Precipitation Anomaly Ratio)
        drought_index = actual_precip / normal_precip
        
        return {
            "source": "AlviaOrange Drought Model",
            "station_id": station_id,
            "year": year,
            "month": month,
            "drought_index": round(drought_index, 3),
            "actual_precipitation_mm": round(actual_precip, 1),
            "normal_precipitation_mm": round(normal_precip, 1),
            "interpretation": "Drier than average" if drought_index < 1.0 else "Wetter than average"
        }

    except Exception as e:
        logger.error(f"Drought index calculation failed for station {station_id}: {e}")
        return {"error": str(e)}


def calculate_fuel_moisture_timeseries(
    station_id: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Calculates daily Fine Fuel & Duff Moisture Codes over a period.

    This is a critical indicator of fire ignition potential. It requires a
    continuous daily weather record to calculate accurately.

    Args:
        station_id: The climate station identifier.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        A dictionary with timeseries data for FFMC and DMC.
    """
    try:
        # Step 1: Fetch daily weather data for the period.
        start_dt = pd.to_datetime(start_date, errors='coerce')
        if pd.isna(start_dt):
            raise ValueError("Invalid start_date format.")
        start_dt_prior = (start_dt - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        
        weather_df = get_station_weather_data(
            station_id, start_dt_prior, end_date, data_type='daily'
        )
        
        if weather_df.empty or len(weather_df) < 2:
            raise Exception("Insufficient historical data for fuel moisture calculation.")

        # Fill missing data with sensible defaults BEFORE iterating
        weather_df = weather_df.fillna({
            'MEAN_TEMPERATURE': 10.0,
            'MEAN_REL_HUMIDITY': 50.0,
            'SPEED_MAX_GUST': 10.0,
            'TOTAL_PRECIPITATION': 0.0
        })

        # Step 2: Initialize moisture codes
        fwi_defaults = fwi_config.FWI_PARAMS
        ffmc_prev = fwi_defaults["ffmc_default"]
        dmc_prev = fwi_defaults["dmc_default"]
        dc_prev = fwi_defaults["dc_default"]

        # Step 3: Iterate through the weather data and calculate daily values
        results = []
        for _, row in weather_df.sort_values('LOCAL_DATE').iterrows():
            fwi_result = calculate_fwi(
                temp=float(row.get('MEAN_TEMPERATURE', 10.0) or 10.0),
                rh=float(row.get('MEAN_REL_HUMIDITY', 50.0) or 50.0),
                wind=float(row.get('SPEED_MAX_GUST', 10.0) or 10.0),
                precip=float(row.get('TOTAL_PRECIPITATION', 0.0) or 0.0),
                ffmc_prev=ffmc_prev,
                dmc_prev=dmc_prev,
                dc_prev=dc_prev
            )
            
            # Update the previous day's codes for the next iteration
            ffmc_prev = fwi_result['ffmc']
            dmc_prev = fwi_result['dmc']
            dc_prev = fwi_result['dc']

            # Only store results for the requested date range
            local_date_ts = row['LOCAL_DATE']
            if pd.notna(local_date_ts) and local_date_ts >= start_dt:
                results.append({
                    "date": local_date_ts.isoformat() if hasattr(local_date_ts, 'isoformat') else str(local_date_ts),
                    "ffmc": fwi_result['ffmc'],
                    "dmc": fwi_result['dmc']
                })

        return {
            "source": "AlviaOrange Fuel Moisture Model",
            "station_id": station_id,
            "start_date": start_date,
            "end_date": end_date,
            "timeseries": results
        }

    except Exception as e:
        logger.error(f"Fuel moisture calculation failed for station {station_id}: {e}")
        return {"error": str(e)}

# ============================================================================
# 2. FIRE SEASON SEVERITY & ANOMALY DETECTION
# ============================================================================

def get_fwi_anomaly(
    station_id: str,
    date_str: str,
) -> Dict[str, Any]:
    """
    Calculates the Fire Weather Index (FWI) anomaly for a specific day.

    This primitive compares the actual FWI for a given day against the
    "normal" FWI, which is calculated using long-term average weather
    for that same day of the year.

    Args:
        station_id: The climate station identifier.
        date_str: The date for the analysis in YYYY-MM-DD format.

    Returns:
        A dictionary with the actual FWI, normal FWI, and the anomaly.
    """
    try:
        target_date = pd.to_datetime(date_str, errors='coerce')
        if pd.isna(target_date):
            raise ValueError("Invalid date format provided.")
        
        month = target_date.month

        # Step 1: Use simplified normal temperatures by month
        monthly_temps = {
            1: -5, 2: -3, 3: 2, 4: 8, 5: 15, 6: 20,
            7: 23, 8: 22, 9: 17, 10: 10, 11: 3, 12: -2
        }
        normal_temp = monthly_temps.get(month, 10.0)

        # Use defaults for other normal weather parameters
        fwi_defaults = fwi_config.FWI_PARAMS
        normal_fwi_result = calculate_fwi(
            temp=normal_temp, rh=60.0, wind=10.0, precip=0.0,
            ffmc_prev=fwi_defaults["ffmc_default"],
            dmc_prev=fwi_defaults["dmc_default"],
            dc_prev=fwi_defaults["dc_default"]
        )
        normal_fwi = normal_fwi_result['fwi']

        # Step 2: Get the actual weather for the target date to calculate actual FWI
        weather_df = get_station_weather_data(station_id, date_str, date_str, data_type='daily')
        if weather_df.empty:
            raise ValueError(f"No historical weather data for {date_str}.")

        actual_weather = weather_df.iloc[0]
        actual_fwi_result = calculate_fwi(
            temp=float(actual_weather.get('MEAN_TEMPERATURE', 10.0) or 10.0),
            rh=float(actual_weather.get('MEAN_REL_HUMIDITY', 50.0) or 50.0),
            wind=float(actual_weather.get('SPEED_MAX_GUST', 10.0) or 10.0),
            precip=float(actual_weather.get('TOTAL_PRECIPITATION', 0.0) or 0.0),
            ffmc_prev=fwi_defaults["ffmc_default"],
            dmc_prev=fwi_defaults["dmc_default"],
            dc_prev=fwi_defaults["dc_default"]
        )
        actual_fwi = actual_fwi_result['fwi']

        # Step 3: Calculate anomaly
        anomaly_absolute = actual_fwi - normal_fwi
        anomaly_percent = (anomaly_absolute / normal_fwi) * 100 if normal_fwi > 0 else 0

        return {
            "source": "AlviaOrange FWI Anomaly Model",
            "station_id": station_id,
            "date": date_str,
            "actual_fwi": round(actual_fwi, 2),
            "normal_fwi_for_doy": round(normal_fwi, 2),
            "anomaly_absolute": round(anomaly_absolute, 2),
            "anomaly_percent": round(anomaly_percent, 2),
            "interpretation": "Higher than normal fire danger" if anomaly_absolute > 0 else "Lower than normal fire danger"
        }

    except Exception as e:
        logger.error(f"FWI anomaly calculation failed for station {station_id}: {e}")
        return {"error": str(e)}

# More analytical primitives to be added below...
# 3. Fire Behavior Prediction
# 4. Geospatial & Risk Analysis 