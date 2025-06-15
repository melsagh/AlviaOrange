Risk Assessment Module
======================

.. automodule:: alviaorange.risk_assessment
   :members:
   :undoc-members:
   :show-inheritance:

The risk assessment module provides comprehensive fire risk calculation and analysis capabilities. It combines weather data, vegetation conditions, and topographical factors to produce accurate fire risk assessments.

Core Functions
--------------

Fire Risk Calculation
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: alviaorange.risk_assessment.calculate_fire_risk_score

This is the primary function for calculating fire risk scores. It integrates multiple data sources and applies sophisticated algorithms to produce reliable risk assessments.

**Example Usage:**

.. code-block:: python

   from alviaorange.risk_assessment import calculate_fire_risk_score
   from datetime import datetime

   # Define zone data
   zone_data = {
       "bounds": {
           "north": 50.0,
           "south": 49.0,
           "east": -120.0,
           "west": -121.0
       },
       "area_km2": 100.0
   }

   # Define weather conditions
   weather_data = {
       "temperature": 35.0,      # High temperature increases risk
       "humidity": 15.0,         # Low humidity increases risk
       "wind_speed": 25.0,       # High wind speed increases risk
       "wind_direction": 225.0,  # Southwest wind
       "precipitation": 0.0,     # No recent precipitation
       "timestamp": datetime.now().isoformat() + 'Z'
   }

   # Define vegetation conditions
   vegetation_data = {
       "moisture_content": 8.0,  # Very dry vegetation
       "fuel_load": 2.5         # Moderate fuel load
   }

   # Calculate risk
   risk_result = calculate_fire_risk_score(
       zone_data=zone_data,
       weather_data=weather_data,
       vegetation_data=vegetation_data
   )

   print(f"Risk Level: {risk_result['risk_level']}")
   print(f"Risk Score: {risk_result['risk_score']}/100")
   print(f"Contributing Factors:")
   for factor, score in risk_result['contributing_factors'].items():
       print(f"  {factor}: {score}")

Weather Index Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: alviaorange.risk_assessment.get_fire_weather_index

Calculates the Fire Weather Index (FWI) based on meteorological conditions.

**Example Usage:**

.. code-block:: python

   from alviaorange.risk_assessment import get_fire_weather_index

   weather_conditions = {
       "temperature": 30.0,
       "humidity": 25.0,
       "wind_speed": 20.0,
       "precipitation": 0.0,
       "timestamp": datetime.now().isoformat() + 'Z'
   }

   fwi_result = get_fire_weather_index(weather_conditions)
   
   print(f"Fire Weather Index: {fwi_result['fwi_value']}")
   print(f"Danger Class: {fwi_result['danger_class']}")
   print(f"Components:")
   print(f"  Fine Fuel Moisture Code: {fwi_result['ffmc']}")
   print(f"  Duff Moisture Code: {fwi_result['dmc']}")
   print(f"  Drought Code: {fwi_result['dc']}")

Risk Assessment Components
--------------------------

Weather Factors
~~~~~~~~~~~~~~~

The risk assessment considers multiple weather factors:

**Temperature**
   - Higher temperatures increase fire risk
   - Critical threshold: 30°C+
   - Extreme conditions: 40°C+

**Humidity**
   - Lower humidity increases fire risk
   - Critical threshold: <30%
   - Extreme conditions: <15%

**Wind Speed**
   - Higher wind speeds increase fire spread risk
   - Critical threshold: 20 km/h+
   - Extreme conditions: 40 km/h+

**Precipitation**
   - Recent precipitation reduces fire risk
   - Significant impact: >5mm in 24 hours
   - Major impact: >20mm in 48 hours

Vegetation Factors
~~~~~~~~~~~~~~~~~~

**Moisture Content**
   - Lower moisture content increases fire risk
   - Critical threshold: <15%
   - Extreme conditions: <8%

**Fuel Load**
   - Higher fuel loads increase fire intensity potential
   - Measured in kg/m²
   - Critical threshold: >2.0 kg/m²

**Vegetation Type**
   - Different vegetation types have different fire characteristics
   - Coniferous forests: Higher risk
   - Grasslands: Fast spread, lower intensity
   - Mixed forests: Variable risk

Topographical Factors
~~~~~~~~~~~~~~~~~~~~~

**Slope**
   - Steeper slopes increase fire spread rate
   - Critical threshold: >30% grade
   - Fire spreads faster uphill

**Aspect**
   - South-facing slopes receive more solar radiation
   - Affects vegetation moisture and fire behavior

**Elevation**
   - Affects weather patterns and vegetation types
   - Higher elevations may have different risk profiles

Risk Calculation Algorithm
--------------------------

The risk calculation uses a weighted scoring system:

.. code-block:: python

   # Simplified risk calculation formula
   base_score = (
       temperature_factor * 0.25 +
       humidity_factor * 0.20 +
       wind_factor * 0.20 +
       vegetation_factor * 0.25 +
       precipitation_factor * 0.10
   )
   
   # Apply modifiers
   final_score = base_score * topographical_modifier
   
   # Determine risk level
   if final_score >= 80:
       risk_level = "EXTREME"
   elif final_score >= 60:
       risk_level = "HIGH"
   elif final_score >= 40:
       risk_level = "MODERATE"
   else:
       risk_level = "LOW"

Performance Targets
-------------------

The risk assessment module is optimized for performance:

* **Risk calculation**: < 10 seconds
* **Weather index calculation**: < 5 seconds
* **Batch processing**: 100+ zones per minute
* **Memory usage**: < 100MB for typical operations

Error Handling
--------------

Comprehensive error handling for various scenarios:

**Data Validation**
   - Invalid coordinate ranges
   - Missing required fields
   - Out-of-range values

**Weather Data Issues**
   - Stale weather data (>6 hours old)
   - Incomplete weather records
   - Extreme weather values

**Calculation Errors**
   - Division by zero protection
   - Overflow/underflow handling
   - NaN value detection

**Example Error Handling:**

.. code-block:: python

   from alviaorange.risk_assessment import calculate_fire_risk_score, RiskAssessmentError

   try:
       result = calculate_fire_risk_score(
           zone_data=invalid_zone,  # This will raise an error
           weather_data=weather_data,
           vegetation_data=vegetation_data
       )
   except RiskAssessmentError as e:
       print(f"Risk assessment failed: {e}")
       # Handle the error appropriately
   except ValueError as e:
       print(f"Invalid input data: {e}")
       # Handle validation errors

Configuration
-------------

The module can be configured using environment variables:

.. code-block:: bash

   # Risk calculation parameters
   export ALVIA_RISK_TEMPERATURE_WEIGHT=0.25
   export ALVIA_RISK_HUMIDITY_WEIGHT=0.20
   export ALVIA_RISK_WIND_WEIGHT=0.20
   export ALVIA_RISK_VEGETATION_WEIGHT=0.25
   export ALVIA_RISK_PRECIPITATION_WEIGHT=0.10
   
   # Thresholds
   export ALVIA_EXTREME_RISK_THRESHOLD=80
   export ALVIA_HIGH_RISK_THRESHOLD=60
   export ALVIA_MODERATE_RISK_THRESHOLD=40

Integration Examples
--------------------

Command Line Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Calculate risk for a specific zone
   python scripts/calculate_risk.py \
     '{"bounds":{"north":50,"south":49,"east":-120,"west":-121},"area_km2":100}' \
     '{"temperature":35,"humidity":15,"wind_speed":25,"wind_direction":225,"precipitation":0,"timestamp":"2024-01-01T12:00:00Z"}' \
     '{"moisture_content":8,"fuel_load":2.5}'

API Integration
~~~~~~~~~~~~~~~

.. code-block:: python

   # For Node.js API integration
   import subprocess
   import json

   def calculate_risk_for_api(zone_data, weather_data, vegetation_data):
       """Wrapper function for API calls."""
       try:
           result = calculate_fire_risk_score(
               zone_data=zone_data,
               weather_data=weather_data,
               vegetation_data=vegetation_data
           )
           return {
               "success": True,
               "data": result
           }
       except Exception as e:
           return {
               "success": False,
               "error": str(e)
           }

Validation and Testing
----------------------

The module includes comprehensive validation:

**Input Validation**
   - All inputs validated using Pydantic schemas
   - Type checking and range validation
   - Required field verification

**Output Validation**
   - Risk scores always between 0-100
   - Risk levels match score ranges
   - All required fields present in output

**Unit Tests**
   - Edge case handling
   - Performance benchmarks
   - Error condition testing

**Integration Tests**
   - End-to-end risk calculation
   - Real-world data scenarios
   - API integration testing 