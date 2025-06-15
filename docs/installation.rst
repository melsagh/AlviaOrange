Installation Guide
==================

This guide covers the installation of AlviaOrange for different use cases and environments.

Requirements
------------

**System Requirements:**

* Python 3.9 or higher
* Operating System: Windows, macOS, or Linux
* Memory: 4GB RAM minimum, 8GB recommended
* Storage: 1GB free space

**Python Dependencies:**

AlviaOrange requires several Python packages that are automatically installed:

* ``pydantic>=2.0.0`` - Data validation and settings management
* ``requests>=2.31.0`` - HTTP library for API calls
* ``pandas>=2.0.0`` - Data manipulation and analysis
* ``numpy>=1.24.0`` - Numerical computing
* ``shapely>=2.0.0`` - Geometric operations
* ``pyproj>=3.6.0`` - Cartographic projections

Installation Methods
--------------------

Method 1: Standard Installation (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For most users, the standard installation is recommended:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/your-username/AlviaOrange.git
   cd AlviaOrange

   # Install dependencies
   pip install -r requirements.txt

   # Verify installation
   python -c "import alviaorange; print('AlviaOrange installed successfully!')"

Method 2: Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For developers who want to contribute or modify the library:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/your-username/AlviaOrange.git
   cd AlviaOrange

   # Install in development mode
   pip install -e .

   # Install development dependencies
   pip install -r requirements-dev.txt

   # Run tests to verify installation
   pytest tests/

Method 3: Virtual Environment (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using a virtual environment is highly recommended to avoid dependency conflicts:

.. code-block:: bash

   # Create virtual environment
   python -m venv alvia_env

   # Activate virtual environment
   # On Windows:
   alvia_env\Scripts\activate
   # On macOS/Linux:
   source alvia_env/bin/activate

   # Install AlviaOrange
   git clone https://github.com/your-username/AlviaOrange.git
   cd AlviaOrange
   pip install -r requirements.txt

Method 4: Conda Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you prefer using Conda:

.. code-block:: bash

   # Create conda environment
   conda create -n alvia python=3.9
   conda activate alvia

   # Install dependencies
   conda install pandas numpy requests shapely pyproj
   pip install pydantic

   # Clone and install AlviaOrange
   git clone https://github.com/your-username/AlviaOrange.git
   cd AlviaOrange

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Set up the following environment variables for optimal functionality:

.. code-block:: bash

   # Optional: NASA FIRMS API key for real satellite data
   export NASA_FIRMS_API_KEY="your_api_key_here"

   # Optional: Custom data directory
   export ALVIA_DATA_DIR="/path/to/data"

   # Optional: Log level
   export ALVIA_LOG_LEVEL="INFO"

API Keys Setup
~~~~~~~~~~~~~~

To access real satellite data, you'll need API keys from various services:

**NASA FIRMS API Key:**

1. Visit `NASA FIRMS <https://firms.modaps.eosdis.nasa.gov/api/>`_
2. Register for an account
3. Generate an API key
4. Set the environment variable: ``NASA_FIRMS_API_KEY``

**OpenWeatherMap API Key (Optional):**

1. Visit `OpenWeatherMap <https://openweathermap.org/api>`_
2. Sign up for a free account
3. Generate an API key
4. Set the environment variable: ``OPENWEATHER_API_KEY``

Verification
------------

Test Basic Functionality
~~~~~~~~~~~~~~~~~~~~~~~~~

Run this test to verify your installation:

.. code-block:: python

   from alviaorange.hotspots import detect_hotspots_for_zone
   from alviaorange.risk_assessment import calculate_fire_risk_score
   from datetime import datetime, timedelta

   # Test hotspot detection
   zone_bounds = {
       'north': 50.0,
       'south': 49.0,
       'east': -120.0,
       'west': -121.0
   }

   end_time = datetime.now()
   start_time = end_time - timedelta(hours=24)
   time_range = {
       'start_date': start_time.isoformat() + 'Z',
       'end_date': end_time.isoformat() + 'Z'
   }

   try:
       result = detect_hotspots_for_zone(
           zone_bounds=zone_bounds,
           time_range=time_range,
           sources=["VIIRS"],
           min_confidence=70
       )
       print(f"✅ Hotspot detection working: {result['total_count']} hotspots found")
   except Exception as e:
       print(f"❌ Hotspot detection failed: {e}")

   # Test risk assessment
   zone_data = {"bounds": zone_bounds, "area_km2": 100.0}
   weather_data = {
       "temperature": 25.0,
       "humidity": 50.0,
       "wind_speed": 10.0,
       "wind_direction": 180.0,
       "precipitation": 0.0,
       "timestamp": datetime.now().isoformat() + 'Z'
   }
   vegetation_data = {"moisture_content": 30.0}

   try:
       risk_result = calculate_fire_risk_score(
           zone_data=zone_data,
           weather_data=weather_data,
           vegetation_data=vegetation_data
       )
       print(f"✅ Risk assessment working: {risk_result['risk_level']} risk level")
   except Exception as e:
       print(f"❌ Risk assessment failed: {e}")

Run Command-Line Scripts
~~~~~~~~~~~~~~~~~~~~~~~~~

Test the command-line interface:

.. code-block:: bash

   # Test hotspot detection script
   cd scripts
   python detect_hotspots.py 50.0 49.0 -120.0 -121.0 "2024-01-01T00:00:00Z" "2024-01-02T00:00:00Z"

   # Test risk assessment script
   python calculate_risk.py '{"bounds":{"north":50,"south":49,"east":-120,"west":-121},"area_km2":100}' '{"temperature":25,"humidity":50,"wind_speed":10,"wind_direction":180,"precipitation":0,"timestamp":"2024-01-01T12:00:00Z"}' '{"moisture_content":30}'

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import Error: No module named 'alviaorange'**

.. code-block:: bash

   # Make sure you're in the correct directory
   cd /path/to/AlviaOrange
   
   # Add to Python path temporarily
   export PYTHONPATH="${PYTHONPATH}:/path/to/AlviaOrange"
   
   # Or install in development mode
   pip install -e .

**Dependency Conflicts**

.. code-block:: bash

   # Create a fresh virtual environment
   python -m venv fresh_env
   source fresh_env/bin/activate  # or fresh_env\Scripts\activate on Windows
   pip install -r requirements.txt

**Permission Errors**

.. code-block:: bash

   # Use --user flag for user-level installation
   pip install --user -r requirements.txt
   
   # Or use sudo on Linux/macOS (not recommended)
   sudo pip install -r requirements.txt

**API Connection Issues**

1. Check your internet connection
2. Verify API keys are set correctly
3. Check firewall settings
4. Try using mock data for testing

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

For better performance, consider installing optional dependencies:

.. code-block:: bash

   # Fast numerical operations
   pip install numba

   # Faster JSON processing
   pip install orjson

   # Memory profiling (development)
   pip install memory-profiler

Docker Installation
-------------------

For containerized deployment:

.. code-block:: dockerfile

   FROM python:3.9-slim

   WORKDIR /app

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       git \
       && rm -rf /var/lib/apt/lists/*

   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application code
   COPY . .

   # Set environment variables
   ENV PYTHONPATH=/app

   # Run tests
   RUN python -c "import alviaorange; print('Installation successful')"

   CMD ["python", "-m", "alviaorange"]

Build and run the Docker container:

.. code-block:: bash

   # Build the image
   docker build -t alviaorange .

   # Run the container
   docker run -it alviaorange

Next Steps
----------

After successful installation:

1. Read the :doc:`quickstart` guide
2. Explore the :doc:`examples/notebooks` 
3. Check out the :doc:`api/modules` reference
4. Join our community discussions

For integration with Node.js applications, see the :doc:`user_guide/integration` guide. 