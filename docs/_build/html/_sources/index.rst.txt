AlviaOrange Documentation
=========================

.. image:: https://img.shields.io/badge/python-3.9+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
   :target: https://your-github-username.github.io/AlviaOrange/
   :alt: Documentation

**AlviaOrange** is an open-source Python library for wildfire detection, risk assessment, and fire behavior analysis. It provides comprehensive tools for data scientists, researchers, and developers working with wildfire monitoring and prediction systems.

🔥 **Key Features**
-------------------

* **Real-time Hotspot Detection**: Integration with NASA FIRMS, VIIRS, and MODIS satellite data
* **Comprehensive Risk Assessment**: Multi-factor fire risk calculation using weather, vegetation, and topographical data
* **Fire Behavior Modeling**: Predict fire spread using advanced algorithms
* **Data Validation**: Robust Pydantic schemas for data integrity
* **API Integration Ready**: Designed for seamless integration with web applications
* **Jupyter Notebook Support**: Perfect for data science workflows

🏗️ **Architecture**
-------------------

AlviaOrange is designed as the core data processing engine for the Alvia platform:

.. code-block:: text

   Frontend (React) → Node.js API → Python AlviaOrange → External Data Sources
                         ↓
                    PostgreSQL Database

The library can be used standalone by data scientists or integrated into larger applications via command-line interfaces.

📚 **Documentation Sections**
-----------------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   tutorials/index

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/hotspot_detection
   user_guide/risk_assessment
   user_guide/data_schemas
   user_guide/integration

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/modules
   api/schemas
   api/hotspots
   api/risk_assessment

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/notebooks
   examples/scripts
   examples/integration

.. toctree::
   :maxdepth: 2
   :caption: Development

   development/contributing
   development/testing
   development/deployment

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   changelog
   license
   support

🚀 **Quick Start**
------------------

Install AlviaOrange:

.. code-block:: bash

   pip install -r requirements.txt

Detect hotspots in a region:

.. code-block:: python

   from alviaorange.hotspots import detect_hotspots_for_zone
   from datetime import datetime, timedelta

   # Define zone bounds
   zone_bounds = {
       'north': 50.0,
       'south': 49.0,
       'east': -120.0,
       'west': -121.0
   }

   # Define time range
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

Calculate fire risk:

.. code-block:: python

   from alviaorange.risk_assessment import calculate_fire_risk_score

   # Define input data
   zone_data = {
       "bounds": zone_bounds,
       "area_km2": 100.0
   }

   weather_data = {
       "temperature": 35.0,
       "humidity": 15.0,
       "wind_speed": 25.0,
       "wind_direction": 225.0,
       "precipitation": 0.0,
       "timestamp": datetime.now().isoformat() + 'Z'
   }

   vegetation_data = {
       "moisture_content": 8.0,
       "fuel_load": 2.5
   }

   # Calculate risk
   risk_result = calculate_fire_risk_score(
       zone_data=zone_data,
       weather_data=weather_data,
       vegetation_data=vegetation_data
   )

   print(f"Risk Level: {risk_result['risk_level']}")
   print(f"Risk Score: {risk_result['risk_score']}/100")

📊 **Performance Targets**
--------------------------

AlviaOrange is designed to meet strict performance requirements:

* **Hotspot Detection**: < 30 seconds for 100km² area
* **Risk Assessment**: < 10 seconds
* **Fire Spread Prediction**: < 60 seconds for 24-hour simulation
* **Weather Data Retrieval**: < 5 seconds

🤝 **Community & Support**
--------------------------

* **GitHub Repository**: `AlviaOrange <https://github.com/your-username/AlviaOrange>`_
* **Issue Tracker**: Report bugs and request features
* **Discussions**: Community support and questions
* **Contributing**: See our :doc:`development/contributing` guide

📄 **License**
--------------

AlviaOrange is released under the MIT License. See :doc:`license` for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 