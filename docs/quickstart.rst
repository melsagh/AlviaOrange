Quick Start Guide
==================

This guide will get you up and running with AlviaOrange in just a few minutes.

Installation
------------

First, install AlviaOrange and its dependencies:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/your-username/AlviaOrange.git
   cd AlviaOrange

   # Install dependencies
   pip install -r requirements.txt

   # Verify installation
   python -c "import alviaorange; print('AlviaOrange ready!')"

Basic Usage
-----------

Detecting Hotspots
~~~~~~~~~~~~~~~~~~

Find wildfire hotspots in a specific area:

.. code-block:: python

   from alviaorange.hotspots import detect_hotspots_for_zone
   from datetime import datetime, timedelta

   # Define the area of interest (British Columbia example)
   zone_bounds = {
       'north': 50.0,
       'south': 49.0,
       'east': -120.0,
       'west': -121.0
   }

   # Look for hotspots in the last 24 hours
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
   for hotspot in result['hotspots'][:5]:  # Show first 5
       print(f"  📍 {hotspot['latitude']:.3f}, {hotspot['longitude']:.3f}")
       print(f"     Confidence: {hotspot['confidence']}%")
       print(f"     Source: {hotspot['source']}")

Calculating Fire Risk
~~~~~~~~~~~~~~~~~~~~~

Assess fire risk for an area:

.. code-block:: python

   from alviaorange.risk_assessment import calculate_fire_risk_score
   from datetime import datetime

   # Define the zone
   zone_data = {
       "bounds": zone_bounds,  # Use the same bounds as above
       "area_km2": 100.0
   }

   # Current weather conditions
   weather_data = {
       "temperature": 32.0,      # Hot day
       "humidity": 20.0,         # Low humidity
       "wind_speed": 15.0,       # Moderate wind
       "wind_direction": 225.0,  # Southwest
       "precipitation": 0.0,     # No rain
       "timestamp": datetime.now().isoformat() + 'Z'
   }

   # Vegetation conditions
   vegetation_data = {
       "moisture_content": 12.0,  # Dry vegetation
       "fuel_load": 2.0          # Moderate fuel load
   }

   # Calculate risk
   risk_result = calculate_fire_risk_score(
       zone_data=zone_data,
       weather_data=weather_data,
       vegetation_data=vegetation_data
   )

   print(f"🔥 Fire Risk Assessment:")
   print(f"   Risk Level: {risk_result['risk_level']}")
   print(f"   Risk Score: {risk_result['risk_score']}/100")
   print(f"   Weather Risk: {risk_result['weather_risk']}")
   print(f"   Vegetation Dryness: {risk_result['vegetation_dryness']}")

Command Line Usage
------------------

AlviaOrange also provides command-line tools for quick operations:

Hotspot Detection
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Detect hotspots in a region
   cd scripts
   python detect_hotspots.py 50.0 49.0 -120.0 -121.0 "2024-01-01T00:00:00Z" "2024-01-02T00:00:00Z"

Risk Assessment
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Calculate fire risk
   python calculate_risk.py \
     '{"bounds":{"north":50,"south":49,"east":-120,"west":-121},"area_km2":100}' \
     '{"temperature":32,"humidity":20,"wind_speed":15,"wind_direction":225,"precipitation":0,"timestamp":"2024-01-01T12:00:00Z"}' \
     '{"moisture_content":12,"fuel_load":2.0}'

Data Validation
---------------

AlviaOrange automatically validates all input data:

.. code-block:: python

   from alviaorange.schemas import Hotspot, WeatherData
   from pydantic import ValidationError
   from datetime import datetime

   # Valid hotspot data
   hotspot = Hotspot(
       latitude=49.5,
       longitude=-120.5,
       confidence=85,
       frp=15.2,
       timestamp=datetime.now(),
       source="VIIRS"
   )
   print(f"✅ Valid hotspot: {hotspot.latitude}, {hotspot.longitude}")

   # Invalid data will raise an error
   try:
       invalid_hotspot = Hotspot(
           latitude=200,  # Invalid: outside valid range
           longitude=-120.5,
           confidence=85,
           frp=15.2,
           timestamp=datetime.now(),
           source="VIIRS"
       )
   except ValidationError as e:
       print(f"❌ Validation error: {e.errors()[0]['msg']}")

Working with Real Data
----------------------

For production use, you'll want to connect to real data sources:

Setting Up API Keys
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Set up NASA FIRMS API key
   export NASA_FIRMS_API_KEY="your_api_key_here"

   # Optional: OpenWeatherMap for weather data
   export OPENWEATHER_API_KEY="your_weather_api_key"

Integration Example
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from alviaorange.hotspots import detect_hotspots_for_zone

   # Check if API key is available
   if os.getenv('NASA_FIRMS_API_KEY'):
       print("🛰️  Using real satellite data")
       # Your detection code here
   else:
       print("🧪 Using mock data for testing")
       # Mock data will be used automatically

Common Patterns
---------------

Monitoring a Region
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from datetime import datetime, timedelta

   def monitor_region(zone_bounds, check_interval_minutes=30):
       """Monitor a region for new hotspots."""
       while True:
           try:
               # Check for hotspots in the last hour
               end_time = datetime.now()
               start_time = end_time - timedelta(hours=1)
               
               result = detect_hotspots_for_zone(
                   zone_bounds=zone_bounds,
                   time_range={
                       'start_date': start_time.isoformat() + 'Z',
                       'end_date': end_time.isoformat() + 'Z'
                   },
                   min_confidence=80
               )
               
               if result['total_count'] > 0:
                   print(f"🚨 Alert: {result['total_count']} new hotspots detected!")
                   for hotspot in result['hotspots']:
                       print(f"   📍 {hotspot['latitude']:.3f}, {hotspot['longitude']:.3f}")
               else:
                   print(f"✅ No new hotspots detected at {datetime.now()}")
               
               # Wait before next check
               time.sleep(check_interval_minutes * 60)
               
           except Exception as e:
               print(f"❌ Error during monitoring: {e}")
               time.sleep(60)  # Wait 1 minute before retrying

   # Start monitoring
   # monitor_region(your_zone_bounds)

Batch Processing
~~~~~~~~~~~~~~~~

.. code-block:: python

   def process_multiple_zones(zones):
       """Process multiple zones for risk assessment."""
       results = []
       
       for zone_name, zone_data in zones.items():
           try:
               # Get current weather (you'd fetch this from a weather API)
               weather_data = get_current_weather(zone_data['bounds'])
               vegetation_data = get_vegetation_data(zone_data['bounds'])
               
               risk_result = calculate_fire_risk_score(
                   zone_data=zone_data,
                   weather_data=weather_data,
                   vegetation_data=vegetation_data
               )
               
               results.append({
                   'zone_name': zone_name,
                   'risk_level': risk_result['risk_level'],
                   'risk_score': risk_result['risk_score']
               })
               
           except Exception as e:
               print(f"❌ Error processing {zone_name}: {e}")
       
       return results

   # Example zones
   zones = {
       'Zone_A': {
           'bounds': {'north': 50, 'south': 49, 'east': -120, 'west': -121},
           'area_km2': 100
       },
       'Zone_B': {
           'bounds': {'north': 51, 'south': 50, 'east': -119, 'west': -120},
           'area_km2': 150
       }
   }

   # results = process_multiple_zones(zones)

Next Steps
----------

Now that you've got the basics down, explore these areas:

📚 **Learn More:**
   - :doc:`api/modules` - Complete API reference
   - :doc:`installation` - Detailed installation guide
   - :doc:`examples/notebooks` - Jupyter notebook examples

🔧 **Integration:**
   - :doc:`user_guide/integration` - Integrate with Node.js APIs
   - Command-line tools for automation
   - Real-time monitoring setups

🤝 **Community:**
   - GitHub repository for issues and contributions
   - Example projects and use cases
   - Community discussions and support

Performance Tips
----------------

For better performance in production:

1. **Use appropriate confidence thresholds**: Higher thresholds = faster processing
2. **Limit time ranges**: Shorter periods = faster queries  
3. **Cache results**: Store results for frequently queried areas
4. **Batch operations**: Process multiple zones together when possible
5. **Monitor API limits**: Respect rate limits for external data sources

Troubleshooting
---------------

**Common Issues:**

❌ **Import errors**: Make sure you're in the correct directory and have installed dependencies

❌ **API connection failures**: Check your internet connection and API keys

❌ **Validation errors**: Check that your input data matches the expected format

❌ **Performance issues**: Reduce the area size or time range for your queries

**Getting Help:**

- Check the error message carefully - AlviaOrange provides detailed error descriptions
- Review the :doc:`api/modules` documentation for function parameters
- Look at the example code in this guide
- Open an issue on GitHub if you find a bug 