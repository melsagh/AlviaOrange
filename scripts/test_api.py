#!/usr/bin/env python3
"""Test script for the enhanced AlviaOrange API endpoints."""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = "http://localhost:8001"
API_KEY = "demo-key"
HEADERS = {"X-API-Key": API_KEY}

def colored_print(message: str, color: str = "white") -> None:
    """Print colored messages to terminal."""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "white": "\033[0m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{message}{colors['reset']}")

def test_endpoint(method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> bool:
    """Test a single API endpoint."""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        colored_print(f"Testing {method} {endpoint}...", "blue")
        
        if method.upper() == "GET":
            response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        else:
            response = requests.request(method.upper(), url, headers=HEADERS, json=params, timeout=10)
        
        if response.status_code == 200:
            colored_print(f"✓ {endpoint} - SUCCESS (Status: {response.status_code})", "green")
            
            # Pretty print JSON response for first few tests
            if endpoint in ["/api/orange/health", "/api/orange/air-quality/scale"]:
                try:
                    data = response.json()
                    colored_print(f"  Response: {json.dumps(data, indent=2)[:200]}...", "white")
                except:
                    colored_print(f"  Response: {response.text[:100]}...", "white")
            
            return True
        else:
            colored_print(f"✗ {endpoint} - FAILED (Status: {response.status_code})", "red")
            colored_print(f"  Response: {response.text[:200]}...", "yellow")
            return False
            
    except requests.exceptions.ConnectionError:
        colored_print(f"✗ {endpoint} - CONNECTION ERROR (Is the server running?)", "red")
        return False
    except requests.exceptions.Timeout:
        colored_print(f"✗ {endpoint} - TIMEOUT", "red")
        return False
    except Exception as e:
        colored_print(f"✗ {endpoint} - ERROR: {str(e)}", "red")
        return False

def main():
    """Run comprehensive API tests."""
    colored_print("🔥 AlviaOrange API Test Suite v2.1.0", "blue")
    colored_print("=" * 50, "blue")
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/api/orange/health", headers=HEADERS, timeout=5)
        if response.status_code != 200:
            colored_print("❌ Server health check failed. Is the server running on port 8001?", "red")
            colored_print("Start the server with: python scripts/run_server.py", "yellow")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        colored_print("❌ Cannot connect to server. Is the server running on port 8001?", "red")
        colored_print("Start the server with: python scripts/run_server.py", "yellow")
        sys.exit(1)
    
    colored_print("✅ Server is running and accessible!", "green")
    colored_print("", "white")
    
    # Test cases
    test_cases = [
        # System Health
        ("GET", "/api/orange/health"),
        
        # Hotspot endpoints
        ("GET", "/api/orange/hotspots"),
        ("GET", "/api/orange/hotspots", {"bbox": "-80.0,43.0,-79.0,44.0"}),
        ("GET", "/api/orange/hotspots/active"),
        ("GET", "/api/orange/hotspots/active", {"bbox": "-80.0,43.0,-79.0,44.0", "hours_back": 48}),
        ("GET", "/api/orange/hotspots/active", {"zone_id": "8f1d823d-4258-4789-902d-1208ebc8bbb7"}),
        ("GET", "/api/orange/hotspots/near", {"lat": 43.6532, "lng": -79.3832, "radius": 25000}),
        
        # Air Quality endpoints
        ("GET", "/api/orange/air-quality"),
        ("GET", "/api/orange/air-quality/scale"),
        ("GET", "/api/orange/air-quality/history", {
            "lat": 43.6532, "lng": -79.3832,
            "start": "2024-01-01T00:00:00Z", "end": "2024-01-31T23:59:59Z"
        }),
        
        # Weather endpoints
        ("GET", "/api/orange/weather/forecast", {"lat": 43.6532, "lng": -79.3832, "days": 7}),
        ("GET", "/api/orange/weather/current", {"lat": 43.6532, "lng": -79.3832}),
        ("GET", "/api/orange/weather/fire-index", {"lat": 43.6532, "lng": -79.3832}),
        
        # Fire Danger endpoints
        ("GET", "/api/orange/fire-danger/risk", {"lat": 43.6532, "lng": -79.3832, "radius": 50000}),
        ("GET", "/api/orange/fire-danger/rating", {"bbox": "-80.0,43.0,-79.0,44.0", "resolution": 1000}),
        
        # Climate endpoints
        ("GET", "/api/orange/climate/stations"),
        ("GET", "/api/orange/climate/stations", {"bbox": "-80.0,43.0,-79.0,44.0"}),
        ("GET", "/api/orange/climate/normals", {"station_id": "6158350", "period": "1991-2020"}),
        
        # Geospatial endpoints
        ("GET", "/api/orange/geospatial/capabilities"),
        ("GET", "/api/orange/wms/tiles/10/256/384", {"layer": "fire-danger", "style": "default"}),
        
        # Zone endpoints
        ("GET", "/api/orange/zones/8f1d823d-4258-4789-902d-1208ebc8bbb7/risk-assessment"),
        ("GET", "/api/orange/zones/8f1d823d-4258-4789-902d-1208ebc8bbb7/monitoring"),
    ]
    
    # Legacy endpoints
    legacy_cases = [
        ("GET", "/hotspots"),
        ("GET", "/air_quality"),
        ("GET", "/air_quality/scale"),
        ("GET", "/air_quality/history", {"city": "Toronto", "start": "2024-01-01"}),
        ("GET", "/cwfis/fwi", {"date": "2024-01-20"}),
        ("GET", "/cwfis/fire_danger", {"date": "2024-01-20"}),
        ("GET", "/cwfis/active_fires"),
    ]
    
    # Run tests
    total_tests = 0
    passed_tests = 0
    
    colored_print("🧪 Testing New API Endpoints:", "blue")
    colored_print("-" * 30, "blue")
    
    for test_case in test_cases:
        if len(test_case) == 2:
            method, endpoint = test_case
            params_dict = None
        else:
            method, endpoint, params_dict = test_case
        
        total_tests += 1
        if test_endpoint(method, endpoint, params_dict):
            passed_tests += 1
        time.sleep(0.1)  # Small delay between requests
    
    colored_print("", "white")
    colored_print("🔄 Testing Legacy Endpoints:", "blue")
    colored_print("-" * 25, "blue")
    
    # Test legacy endpoints without authentication
    headers_no_auth = {}
    original_headers = HEADERS.copy()
    
    for test_case in legacy_cases:
        if len(test_case) == 2:
            method, endpoint = test_case
            params_dict = None
        else:
            method, endpoint, params_dict = test_case
        
        total_tests += 1
        
        # Test without auth for legacy endpoints
        global HEADERS
        HEADERS = headers_no_auth
        
        if test_endpoint(method, endpoint, params_dict):
            passed_tests += 1
        time.sleep(0.1)
    
    # Restore headers
    HEADERS = original_headers
    
    # Summary
    colored_print("", "white")
    colored_print("📊 Test Summary:", "blue")
    colored_print("=" * 15, "blue")
    colored_print(f"Total Tests: {total_tests}", "white")
    colored_print(f"Passed: {passed_tests}", "green")
    colored_print(f"Failed: {total_tests - passed_tests}", "red")
    colored_print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%", "blue")
    
    if passed_tests == total_tests:
        colored_print("", "white")
        colored_print("🎉 All tests passed! The AlviaOrange API is working correctly.", "green")
        colored_print("", "white")
        colored_print("Next steps:", "blue")
        colored_print("• Visit http://localhost:8001/api/orange/docs for interactive documentation", "white")
        colored_print("• Check out the API guide: docs/API_GUIDE.md", "white")
        colored_print("• Start integrating with your Alvia Platform!", "white")
    else:
        colored_print("", "white")
        colored_print("⚠️ Some tests failed. Check the server logs for details.", "yellow")
        sys.exit(1)

def test_authentication():
    """Test authentication failures."""
    colored_print("", "white")
    colored_print("🔐 Testing Authentication:", "blue")
    colored_print("-" * 25, "blue")
    
    # Test without API key
    try:
        response = requests.get(f"{API_BASE_URL}/api/orange/health", timeout=5)
        if response.status_code == 401:
            colored_print("✓ Authentication required - SUCCESS", "green")
        else:
            colored_print(f"✗ Expected 401, got {response.status_code}", "red")
    except Exception as e:
        colored_print(f"✗ Auth test failed: {str(e)}", "red")
    
    # Test with invalid API key
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/orange/health", 
            headers={"X-API-Key": "invalid-key"}, 
            timeout=5
        )
        if response.status_code == 401:
            colored_print("✓ Invalid API key rejected - SUCCESS", "green")
        else:
            colored_print(f"✗ Expected 401, got {response.status_code}", "red")
    except Exception as e:
        colored_print(f"✗ Invalid key test failed: {str(e)}", "red")

if __name__ == "__main__":
    main()
    test_authentication() 