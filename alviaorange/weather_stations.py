"""Weather station data retrieval and spatial matching functionality.

This module provides tools for:
- Fetching climate station data from Weather.gc.ca API
- Finding nearest weather stations to geographic points or shapefiles
- Retrieving weather data from specific stations
"""

from __future__ import annotations

import json
import requests
import pandas as pd
import geopandas as gpd
from typing import Dict, List, Any, Optional, Tuple
from geopy.distance import geodesic
import numpy as np

BASE_API_URL = "https://api.weather.gc.ca"


def fetch_climate_stations(
    province: Optional[str] = None,
    limit: int = 500,
    active_only: bool = True
) -> gpd.GeoDataFrame:
    """Fetch climate stations from Weather.gc.ca API.
    
    Parameters
    ----------
    province : str, optional
        Filter by province code (e.g., 'BC', 'ON', 'QC')
    limit : int, default 500
        Maximum number of stations to retrieve per request
    active_only : bool, default True
        If True, only return stations with recent data
        
    Returns
    -------
    geopandas.GeoDataFrame
        Climate stations with geometry and metadata
    """
    
    all_stations = []
    offset = 0
    
    while True:
        params = {
            'f': 'json',
            'lang': 'en',
            'limit': limit,
            'offset': offset
        }
        
        if province:
            params['PROV_STATE_TERR_CODE'] = province.upper()
            
        response = requests.get(
            f"{BASE_API_URL}/collections/climate-stations/items",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        features = data.get('features', [])
        
        if not features:
            break
            
        all_stations.extend(features)
        
        # Check if we've retrieved all available data
        if len(features) < limit:
            break
            
        offset += limit
        
    if not all_stations:
        return gpd.GeoDataFrame()
    
    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(all_stations, crs='EPSG:4326')
    
    # Filter for active stations if requested
    if active_only:
        # Keep stations that have data after 2020
        gdf['LAST_DATE'] = pd.to_datetime(gdf['LAST_DATE'], errors='coerce')
        gdf = gdf[gdf['LAST_DATE'] >= '2020-01-01']
    
    return gdf


def find_nearest_stations(
    shapefile_path: str = None,
    point_coords: Tuple[float, float] = None,
    k: int = 5,
    max_distance_km: float = 100,
    province: Optional[str] = None
) -> gpd.GeoDataFrame:
    """Find k-nearest weather stations to a point or shapefile.
    
    Parameters
    ----------
    shapefile_path : str, optional
        Path to shapefile (uses centroid if polygon)
    point_coords : tuple of (lon, lat), optional
        Point coordinates to search from
    k : int, default 5
        Number of nearest stations to return
    max_distance_km : float, default 100
        Maximum distance in kilometers
    province : str, optional
        Filter stations by province
        
    Returns
    -------
    geopandas.GeoDataFrame
        Nearest weather stations with distance information
    """
    
    if shapefile_path is None and point_coords is None:
        raise ValueError("Must provide either shapefile_path or point_coords")
    
    # Get reference point
    if shapefile_path:
        shapes = gpd.read_file(shapefile_path)
        if shapes.crs != 'EPSG:4326':
            shapes = shapes.to_crs('EPSG:4326')
        
        # Use centroid of first feature
        ref_point = shapes.geometry.iloc[0].centroid
        ref_coords = (ref_point.y, ref_point.x)  # (lat, lon) for geopy
    else:
        ref_coords = (point_coords[1], point_coords[0])  # Convert (lon, lat) to (lat, lon)
    
    # Fetch stations
    stations = fetch_climate_stations(province=province)
    
    if stations.empty:
        return gpd.GeoDataFrame()
    
    # Calculate distances
    distances = []
    for idx, station in stations.iterrows():
        station_coords = (station.geometry.y, station.geometry.x)
        distance = geodesic(ref_coords, station_coords).kilometers
        distances.append(distance)
    
    stations['distance_km'] = distances
    
    # Filter by maximum distance and get k nearest
    nearby_stations = stations[stations['distance_km'] <= max_distance_km]
    nearest_stations = nearby_stations.nsmallest(k, 'distance_km')
    
    return nearest_stations


def get_station_weather_data(
    station_id: str,
    start_date: str,
    end_date: str,
    data_type: str = 'daily'
) -> pd.DataFrame:
    """Get weather data for a specific station.
    
    Parameters
    ----------
    station_id : str
        Climate identifier for the station
    start_date : str
        Start date in YYYY-MM-DD format
    end_date : str
        End date in YYYY-MM-DD format
    data_type : str, default 'daily'
        Type of data: 'daily', 'monthly', or 'hourly'
        
    Returns
    -------
    pandas.DataFrame
        Weather data for the specified period
    """
    
    # Map data types to API endpoints
    endpoint_map = {
        'daily': 'climate-daily',
        'monthly': 'climate-monthly', 
        'hourly': 'climate-hourly'
    }
    
    if data_type not in endpoint_map:
        raise ValueError(f"data_type must be one of {list(endpoint_map.keys())}")
    
    params = {
        'f': 'json',
        'lang': 'en',
        'CLIMATE_IDENTIFIER': station_id,
        'datetime': f"{start_date}/{end_date}"
    }
    
    response = requests.get(
        f"{BASE_API_URL}/collections/{endpoint_map[data_type]}/items",
        params=params,
        timeout=30
    )
    response.raise_for_status()
    
    data = response.json()
    features = data.get('features', [])
    
    if not features:
        return pd.DataFrame()
    
    # Extract properties and convert to DataFrame
    records = [feature['properties'] for feature in features]
    df = pd.DataFrame(records)
    
    # Convert LOCAL_DATE to datetime if present
    if 'LOCAL_DATE' in df.columns:
        df['LOCAL_DATE'] = pd.to_datetime(df['LOCAL_DATE'])
        df = df.sort_values('LOCAL_DATE')
    
    return df


def get_multi_station_data(
    station_ids: List[str],
    start_date: str,
    end_date: str,
    data_type: str = 'daily',
    aggregate_method: str = 'mean'
) -> pd.DataFrame:
    """Get weather data from multiple stations and optionally aggregate.
    
    Parameters
    ----------
    station_ids : list of str
        List of climate identifiers
    start_date : str
        Start date in YYYY-MM-DD format
    end_date : str
        End date in YYYY-MM-DD format
    data_type : str, default 'daily'
        Type of data: 'daily', 'monthly', or 'hourly'
    aggregate_method : str, default 'mean'
        How to aggregate data: 'mean', 'median', 'min', 'max', or 'none'
        
    Returns
    -------
    pandas.DataFrame
        Combined weather data, optionally aggregated
    """
    
    all_data = []
    
    for station_id in station_ids:
        try:
            station_data = get_station_weather_data(
                station_id, start_date, end_date, data_type
            )
            if not station_data.empty:
                station_data['STATION_ID'] = station_id
                all_data.append(station_data)
        except Exception as e:
            print(f"Warning: Could not retrieve data for station {station_id}: {e}")
            continue
    
    if not all_data:
        return pd.DataFrame()
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    if aggregate_method == 'none':
        return combined_df
    
    # Aggregate numeric columns by date
    numeric_columns = combined_df.select_dtypes(include=[np.number]).columns
    date_column = 'LOCAL_DATE' if 'LOCAL_DATE' in combined_df.columns else None
    
    if date_column and not numeric_columns.empty:
        agg_func = getattr(combined_df.groupby(date_column)[numeric_columns], aggregate_method)
        aggregated = agg_func().reset_index()
        return aggregated
    
    return combined_df


def weather_station_workflow(
    shapefile_path: str = None,
    point_coords: Tuple[float, float] = None,
    k: int = 3,
    start_date: str = '2023-01-01',
    end_date: str = '2023-12-31',
    data_type: str = 'daily',
    aggregate_method: str = 'mean',
    max_distance_km: float = 50,
    province: Optional[str] = None
) -> Tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """Complete workflow: find nearest stations and get their weather data.
    
    Parameters
    ----------
    shapefile_path : str, optional
        Path to shapefile
    point_coords : tuple of (lon, lat), optional
        Point coordinates
    k : int, default 3
        Number of nearest stations
    start_date : str, default '2023-01-01'
        Start date for weather data
    end_date : str, default '2023-12-31'
        End date for weather data
    data_type : str, default 'daily'
        Type of weather data
    aggregate_method : str, default 'mean'
        Aggregation method for multiple stations
    max_distance_km : float, default 50
        Maximum distance to search for stations
    province : str, optional
        Province filter
        
    Returns
    -------
    tuple of (GeoDataFrame, DataFrame)
        Nearest stations and their weather data
    """
    
    # Find nearest stations
    nearest_stations = find_nearest_stations(
        shapefile_path=shapefile_path,
        point_coords=point_coords,
        k=k,
        max_distance_km=max_distance_km,
        province=province
    )
    
    if nearest_stations.empty:
        return nearest_stations, pd.DataFrame()
    
    # Get weather data
    station_ids = nearest_stations['CLIMATE_IDENTIFIER'].tolist()
    weather_data = get_multi_station_data(
        station_ids=station_ids,
        start_date=start_date,
        end_date=end_date,
        data_type=data_type,
        aggregate_method=aggregate_method
    )
    
    return nearest_stations, weather_data 