API Reference
=============

This section contains the complete API reference for AlviaOrange, automatically generated from the source code docstrings.

Overview
--------

AlviaOrange is organized into several key modules:

* :doc:`schemas` - Data validation and type definitions using Pydantic
* :doc:`hotspots` - Wildfire hotspot detection and management
* :doc:`risk_assessment` - Fire risk calculation and analysis

All functions include comprehensive type hints and validation to ensure data integrity and provide excellent developer experience.

Core Modules
------------

.. toctree::
   :maxdepth: 2

   schemas
   hotspots
   risk_assessment

Module Index
------------

.. autosummary::
   :toctree: _autosummary
   :template: module.rst
   :recursive:

   alviaorange.schemas
   alviaorange.hotspots
   alviaorange.risk_assessment

Quick Reference
---------------

**Hotspot Detection Functions:**

.. autosummary::

   alviaorange.hotspots.detect_hotspots_for_zone
   alviaorange.hotspots.get_active_hotspots
   alviaorange.hotspots.get_hotspots_near_point

**Risk Assessment Functions:**

.. autosummary::

   alviaorange.risk_assessment.calculate_fire_risk_score

**Core Data Models:**

.. autosummary::

   alviaorange.schemas.Hotspot
   alviaorange.schemas.RiskAssessment
   alviaorange.schemas.WeatherData
   alviaorange.schemas.VegetationData
   alviaorange.schemas.ZoneBounds

Performance Notes
-----------------

All functions are designed to meet specific performance targets:

* **Hotspot detection**: < 30 seconds for 100km² area
* **Risk assessment**: < 10 seconds
* **Data validation**: < 1 second for typical payloads

Error Handling
--------------

All functions use consistent error handling patterns:

* **Input validation**: Pydantic models validate all inputs
* **Custom exceptions**: Specific exception types for different error conditions
* **Detailed error messages**: Clear descriptions of what went wrong
* **Graceful degradation**: Functions continue working with partial data when possible

Type Safety
-----------

AlviaOrange is fully typed using Python type hints:

* All function parameters and return values are typed
* Pydantic models provide runtime type validation
* IDE support for autocompletion and error detection
* MyPy compatibility for static type checking 