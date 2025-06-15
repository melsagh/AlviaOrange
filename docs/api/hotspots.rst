Hotspots Module
===============

.. automodule:: alviaorange.hotspots
   :members:
   :undoc-members:
   :show-inheritance:

The hotspots module provides comprehensive functionality for detecting and managing wildfire hotspots from various satellite data sources.

Core Functions
--------------

Hotspot Detection
~~~~~~~~~~~~~~~~~

.. autofunction:: alviaorange.hotspots.detect_hotspots_for_zone

This is the primary function for detecting hotspots within a geographical zone. It integrates with multiple satellite data sources and provides comprehensive filtering and validation.

**Example Usage:**

.. code-block:: python

   from alviaorange.hotspots import detect_hotspots_for_zone
   from datetime import datetime, timedelta

   # Define zone bounds (British Columbia example)
   zone_bounds = {
       'north': 50.0,
       'south': 49.0,
       'east': -120.0,
       'west': -121.0
   }

   # Define time range for last 24 hours
   end_time = datetime.now()
   start_time = end_time - timedelta(hours=24)
   time_range = {
       'start_date': start_time.isoformat() + 'Z',
       'end_date': end_time.isoformat() + 'Z'
   }

   # Detect hotspots
   result = detect_hotspots_for_zone(
       zone_bounds=zone_bounds,
       time_range=time_range,
       sources=["VIIRS", "MODIS"],
       min_confidence=70
   )

   print(f"Found {result['total_count']} hotspots")
   for hotspot in result['hotspots']:
       print(f"  {hotspot['latitude']:.3f}, {hotspot['longitude']:.3f} - {hotspot['confidence']}%")

Active Hotspots
~~~~~~~~~~~~~~~

.. autofunction:: alviaorange.hotspots.get_active_hotspots

Retrieves currently active hotspots within a specified time window.

**Example Usage:**

.. code-block:: python

   from alviaorange.hotspots import get_active_hotspots

   # Get hotspots from last 48 hours
   active_hotspots = get_active_hotspots(
       zone_bounds=zone_bounds,
       hours_back=48,
       min_confidence=80
   )

   print(f"Active hotspots: {active_hotspots['total_count']}")

Proximity Search
~~~~~~~~~~~~~~~~

.. autofunction:: alviaorange.hotspots.get_hotspots_near_point

Finds hotspots within a specified radius of a point of interest.

**Example Usage:**

.. code-block:: python

   from alviaorange.hotspots import get_hotspots_near_point

   # Find hotspots within 50km of a specific location
   nearby_hotspots = get_hotspots_near_point(
       lat=49.5,
       lng=-120.5,
       radius_km=50,
       limit=10
   )

   print(f"Nearby hotspots: {nearby_hotspots['total_count']}")

Utility Functions
-----------------

Internal Helper Functions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: alviaorange.hotspots._fetch_hotspots_from_source

.. autofunction:: alviaorange.hotspots._remove_duplicate_hotspots

.. autofunction:: alviaorange.hotspots._calculate_distance

Exception Classes
-----------------

.. autoexception:: alviaorange.hotspots.HotspotDetectionError

.. autoexception:: alviaorange.hotspots.APIConnectionError

Data Sources
------------

The hotspots module integrates with several satellite data sources:

**NASA FIRMS (Fire Information for Resource Management System)**
   - Real-time and near real-time fire detection
   - Global coverage
   - Multiple satellite platforms

**VIIRS (Visible Infrared Imaging Radiometer Suite)**
   - High-resolution fire detection
   - 375m pixel resolution
   - NOAA-20 and Suomi NPP satellites

**MODIS (Moderate Resolution Imaging Spectroradiometer)**
   - Established fire detection system
   - 1km pixel resolution
   - Terra and Aqua satellites

**Global Forest Watch (GFW)**
   - Forest fire alerts
   - Deforestation monitoring
   - Historical fire data

Configuration
-------------

The module can be configured using environment variables:

.. code-block:: bash

   # NASA FIRMS API key
   export NASA_FIRMS_API_KEY="your_api_key_here"
   
   # Default confidence threshold
   export ALVIA_DEFAULT_CONFIDENCE=70
   
   # Request timeout (seconds)
   export ALVIA_REQUEST_TIMEOUT=30

Performance Considerations
--------------------------

**Optimization Tips:**

1. **Use appropriate time ranges**: Shorter time ranges result in faster queries
2. **Filter by confidence**: Higher confidence thresholds reduce processing time
3. **Limit data sources**: Use only necessary sources for your use case
4. **Cache results**: Implement caching for frequently requested areas

**Performance Targets:**

- Zone detection (100km²): < 30 seconds
- Point proximity search: < 10 seconds
- Active hotspots retrieval: < 15 seconds

Error Handling
--------------

The module implements comprehensive error handling:

**Input Validation:**
   - Geographic bounds validation
   - Date range validation
   - Parameter type checking

**API Error Handling:**
   - Network timeout handling
   - Rate limit management
   - Service unavailability handling

**Data Quality Checks:**
   - Duplicate detection and removal
   - Confidence score validation
   - Coordinate validation

**Example Error Handling:**

.. code-block:: python

   from alviaorange.hotspots import detect_hotspots_for_zone, HotspotDetectionError

   try:
       result = detect_hotspots_for_zone(
           zone_bounds=invalid_bounds,  # This will raise an error
           time_range=time_range
       )
   except HotspotDetectionError as e:
       print(f"Detection failed: {e}")
       # Handle the error appropriately
   except ValueError as e:
       print(f"Invalid input: {e}")
       # Handle validation errors 