Schemas Module
==============

.. automodule:: alviaorange.schemas
   :members:
   :undoc-members:
   :show-inheritance:

The schemas module provides comprehensive data validation and type definitions using Pydantic models. All data structures used throughout AlviaOrange are defined here to ensure data integrity and provide excellent developer experience.

Core Data Models
----------------

Geographic Data
~~~~~~~~~~~~~~~

.. autoclass:: alviaorange.schemas.ZoneBounds
   :members:
   :undoc-members:

.. autoclass:: alviaorange.schemas.Coordinates
   :members:
   :undoc-members:

Hotspot Data
~~~~~~~~~~~~

.. autoclass:: alviaorange.schemas.Hotspot
   :members:
   :undoc-members:

.. autoclass:: alviaorange.schemas.HotspotSource
   :members:
   :undoc-members:

Weather Data
~~~~~~~~~~~~

.. autoclass:: alviaorange.schemas.WeatherData
   :members:
   :undoc-members:

.. autoclass:: alviaorange.schemas.FireWeatherIndex
   :members:
   :undoc-members:

Risk Assessment
~~~~~~~~~~~~~~~

.. autoclass:: alviaorange.schemas.RiskAssessment
   :members:
   :undoc-members:

.. autoclass:: alviaorange.schemas.RiskLevel
   :members:
   :undoc-members:

Vegetation Data
~~~~~~~~~~~~~~~

.. autoclass:: alviaorange.schemas.VegetationData
   :members:
   :undoc-members:

.. autoclass:: alviaorange.schemas.DrynessLevel
   :members:
   :undoc-members:

Time Range
~~~~~~~~~~

.. autoclass:: alviaorange.schemas.TimeRange
   :members:
   :undoc-members:

Usage Examples
--------------

Creating and Validating Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from alviaorange.schemas import Hotspot, WeatherData, ZoneBounds
   from datetime import datetime

   # Create a hotspot with validation
   hotspot = Hotspot(
       latitude=49.5,
       longitude=-120.5,
       confidence=85,
       brightness=320.5,
       scan_time=datetime.now(),
       satellite="VIIRS",
       source="NASA_FIRMS"
   )

   # Create weather data
   weather = WeatherData(
       temperature=35.0,
       humidity=15.0,
       wind_speed=25.0,
       wind_direction=225.0,
       precipitation=0.0,
       timestamp=datetime.now()
   )

   # Create zone bounds
   zone = ZoneBounds(
       north=50.0,
       south=49.0,
       east=-120.0,
       west=-121.0
   )

   print(f"Hotspot: {hotspot.latitude}, {hotspot.longitude}")
   print(f"Weather: {weather.temperature}°C, {weather.humidity}% humidity")
   print(f"Zone area: {zone.area_km2:.1f} km²")

Data Validation
~~~~~~~~~~~~~~~

Pydantic automatically validates all data:

.. code-block:: python

   from alviaorange.schemas import Hotspot
   from pydantic import ValidationError

   try:
       # This will raise a validation error
       invalid_hotspot = Hotspot(
           latitude=200,  # Invalid: must be between -90 and 90
           longitude=-120.5,
           confidence=85,
           brightness=320.5,
           scan_time="invalid-date",  # Invalid: must be datetime
           satellite="VIIRS",
           source="NASA_FIRMS"
       )
   except ValidationError as e:
       print(f"Validation error: {e}")

JSON Serialization
~~~~~~~~~~~~~~~~~~

All models support JSON serialization:

.. code-block:: python

   from alviaorange.schemas import WeatherData
   from datetime import datetime
   import json

   weather = WeatherData(
       temperature=25.0,
       humidity=60.0,
       wind_speed=10.0,
       wind_direction=180.0,
       precipitation=0.0,
       timestamp=datetime.now()
   )

   # Convert to JSON
   weather_json = weather.model_dump_json()
   print(weather_json)

   # Parse from JSON
   weather_dict = json.loads(weather_json)
   weather_restored = WeatherData(**weather_dict)

Validation Rules
----------------

Geographic Coordinates
~~~~~~~~~~~~~~~~~~~~~~

* **Latitude**: Must be between -90.0 and 90.0 degrees
* **Longitude**: Must be between -180.0 and 180.0 degrees
* **Zone bounds**: North must be greater than south, east must be greater than west

Confidence Scores
~~~~~~~~~~~~~~~~~

* **Range**: 0 to 100 (integer)
* **Minimum recommended**: 50 for reliable detections
* **High confidence**: 80+ for critical applications

Weather Data
~~~~~~~~~~~~

* **Temperature**: Celsius, typically -50 to 60°C
* **Humidity**: Percentage, 0 to 100
* **Wind speed**: km/h, 0 to 200
* **Wind direction**: Degrees, 0 to 360
* **Precipitation**: mm, 0 to 1000

Risk Levels
~~~~~~~~~~~

* **LOW**: Minimal fire risk
* **MODERATE**: Some fire risk, monitor conditions
* **HIGH**: Significant fire risk, prepare for action
* **EXTREME**: Critical fire risk, immediate action required

Error Handling
--------------

All schemas provide detailed error messages for validation failures:

.. code-block:: python

   from alviaorange.schemas import RiskAssessment
   from pydantic import ValidationError

   try:
       risk = RiskAssessment(
           risk_score=150,  # Invalid: must be 0-100
           risk_level="INVALID",  # Invalid: must be valid enum
           zone_id="test-zone",
           timestamp="not-a-date"  # Invalid: must be datetime
       )
   except ValidationError as e:
       for error in e.errors():
           print(f"Field: {error['loc']}")
           print(f"Error: {error['msg']}")
           print(f"Value: {error['input']}")

Type Safety
-----------

All schemas are fully typed and support:

* **IDE autocompletion**: Full IntelliSense support
* **Static type checking**: MyPy compatibility
* **Runtime validation**: Automatic data validation
* **Documentation**: Auto-generated from type hints

Performance
-----------

Pydantic models are optimized for performance:

* **Fast validation**: Rust-based validation engine
* **Memory efficient**: Minimal memory overhead
* **Serialization**: Fast JSON encoding/decoding
* **Caching**: Validation rules are cached for reuse 