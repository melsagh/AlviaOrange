#!/usr/bin/env python3
"""
Command-line wrapper for hotspot detection.

This script is designed to be called by the Node.js API server using python-shell.
It accepts command-line arguments, processes them, calls the appropriate library
function, and outputs the result as JSON to stdout.

Usage:
    python detect_hotspots.py <north> <south> <east> <west> <start_date> <end_date> [sources] [min_confidence] [api_key]

Example:
    python detect_hotspots.py 45.0 44.0 -121.0 -122.0 "2024-01-01T00:00:00Z" "2024-01-02T00:00:00Z" "VIIRS,MODIS" 70 "your_api_key"
"""

import sys
import json
import logging
from datetime import datetime

# Add the parent directory to the path to import alviaorange
sys.path.insert(0, '..')

try:
    from alviaorange.hotspots import detect_hotspots_for_zone, HotspotDetectionError
except ImportError as e:
    error_response = {
        "success": False,
        "error": f"Failed to import alviaorange module: {str(e)}",
        "hotspots": [],
        "total_count": 0
    }
    print(json.dumps(error_response))
    sys.exit(1)

def main():
    """Main function to process command-line arguments and call hotspot detection."""
    
    # Configure logging to stderr so it doesn't interfere with JSON output
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    
    try:
        # Parse command-line arguments
        if len(sys.argv) < 7:
            raise ValueError(
                "Insufficient arguments. Required: north, south, east, west, start_date, end_date"
            )
        
        north = float(sys.argv[1])
        south = float(sys.argv[2])
        east = float(sys.argv[3])
        west = float(sys.argv[4])
        start_date = sys.argv[5]
        end_date = sys.argv[6]
        
        # Optional arguments
        sources = sys.argv[7].split(',') if len(sys.argv) > 7 else ["VIIRS", "MODIS", "FIRMS"]
        min_confidence = int(sys.argv[8]) if len(sys.argv) > 8 else 70
        api_key = sys.argv[9] if len(sys.argv) > 9 else None
        
        # Prepare arguments for the function
        zone_bounds = {
            'north': north,
            'south': south,
            'east': east,
            'west': west
        }
        
        time_range = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        # Call the hotspot detection function
        result = detect_hotspots_for_zone(
            zone_bounds=zone_bounds,
            time_range=time_range,
            sources=sources,
            min_confidence=min_confidence,
            api_key=api_key
        )
        
        # Add success flag to the result
        result['success'] = True
        
        # Output the result as JSON
        print(json.dumps(result, default=str))
        
    except ValueError as e:
        error_response = {
            "success": False,
            "error": f"Invalid input parameters: {str(e)}",
            "hotspots": [],
            "total_count": 0
        }
        print(json.dumps(error_response))
        sys.exit(1)
        
    except HotspotDetectionError as e:
        error_response = {
            "success": False,
            "error": f"Hotspot detection failed: {str(e)}",
            "hotspots": [],
            "total_count": 0
        }
        print(json.dumps(error_response))
        sys.exit(1)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "hotspots": [],
            "total_count": 0
        }
        print(json.dumps(error_response))
        sys.exit(1)

if __name__ == "__main__":
    main() 