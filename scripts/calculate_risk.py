#!/usr/bin/env python3
"""
Command-line wrapper for fire risk assessment calculation.

This script is designed to be called by the Node.js API server using python-shell.
It accepts JSON input via command-line arguments, processes it, calls the appropriate
library function, and outputs the result as JSON to stdout.

Usage:
    python calculate_risk.py '<zone_data_json>' '<weather_data_json>' '<vegetation_data_json>' [topography_data_json]

Example:
    python calculate_risk.py '{"bounds":{"north":45,"south":44,"east":-121,"west":-122},"area_km2":100}' '{"temperature":35,"humidity":15,"wind_speed":25,"wind_direction":225,"precipitation":0,"timestamp":"2024-01-01T12:00:00Z"}' '{"ndvi":0.3,"moisture_content":8,"fuel_load":2.5}'
"""

import sys
import json
import logging
from datetime import datetime

# Add the parent directory to the path to import alviaorange
sys.path.insert(0, '..')

try:
    from alviaorange.risk_assessment import calculate_fire_risk_score, RiskAssessmentError
except ImportError as e:
    error_response = {
        "success": False,
        "error": f"Failed to import alviaorange module: {str(e)}",
        "risk_score": 0,
        "risk_level": "low"
    }
    print(json.dumps(error_response))
    sys.exit(1)

def main():
    """Main function to process command-line arguments and call risk assessment."""
    
    # Configure logging to stderr so it doesn't interfere with JSON output
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    
    try:
        # Parse command-line arguments
        if len(sys.argv) < 4:
            raise ValueError(
                "Insufficient arguments. Required: zone_data_json, weather_data_json, vegetation_data_json"
            )
        
        zone_data_json = sys.argv[1]
        weather_data_json = sys.argv[2]
        vegetation_data_json = sys.argv[3]
        topography_data_json = sys.argv[4] if len(sys.argv) > 4 else None
        
        # Parse JSON arguments
        try:
            zone_data = json.loads(zone_data_json)
            weather_data = json.loads(weather_data_json)
            vegetation_data = json.loads(vegetation_data_json)
            topography_data = json.loads(topography_data_json) if topography_data_json else None
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON input: {str(e)}")
        
        # Call the risk assessment function
        result = calculate_fire_risk_score(
            zone_data=zone_data,
            weather_data=weather_data,
            vegetation_data=vegetation_data,
            topography_data=topography_data
        )
        
        # Add success flag to the result
        result['success'] = True
        
        # Output the result as JSON
        print(json.dumps(result, default=str))
        
    except ValueError as e:
        error_response = {
            "success": False,
            "error": f"Invalid input parameters: {str(e)}",
            "risk_score": 0,
            "risk_level": "low",
            "recommendations": []
        }
        print(json.dumps(error_response))
        sys.exit(1)
        
    except RiskAssessmentError as e:
        error_response = {
            "success": False,
            "error": f"Risk assessment failed: {str(e)}",
            "risk_score": 0,
            "risk_level": "low",
            "recommendations": []
        }
        print(json.dumps(error_response))
        sys.exit(1)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "risk_score": 0,
            "risk_level": "low",
            "recommendations": []
        }
        print(json.dumps(error_response))
        sys.exit(1)

if __name__ == "__main__":
    main() 