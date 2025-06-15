# AlviaOrange - Open-Source Python Core Library

This repository contains the core data processing and analysis logic for the Alvia platform. It integrates with external data sources to provide wildfire detection, risk assessment, and fire behavior modeling capabilities.

## 🏗️ Architecture
```
Frontend (React) → Node.js API → Python AlviaOrange → External Data Sources
                      ↓
                 PostgreSQL Database
```

---

## 🔴 CRITICAL - MVP Phase 1 (Must Have)

### 1. Core Hotspot Detection
- [ ] **`detect_hotspots_for_zone(zone_bounds, time_range, sources)`**
  - [ ] Implement function in `alviaorange/hotspots.py`
  - [ ] Add Pydantic models for zone bounds and hotspot data
  - [ ] Integrate with NASA FIRMS API
  - [ ] Integrate with NOAA/VIIRS data
  - [ ] Create command-line wrapper script `scripts/detect_hotspots.py`
  - [ ] Add comprehensive error handling and validation

- [ ] **`get_active_hotspots(zone_bounds, hours_back)`**
  - [ ] Filter hotspots by recency (24-48 hours)
  - [ ] Implement confidence threshold filtering
  - [ ] Create wrapper script `scripts/get_active_hotspots.py`

### 2. Risk Assessment System
- [ ] **`calculate_fire_risk_score(zone_data, weather_data, vegetation_data)`**
  - [ ] Create `alviaorange/risk_assessment.py` module
  - [ ] Implement multi-factor risk calculation algorithm
  - [ ] Add Pydantic models for weather and vegetation data
  - [ ] Include risk level categorization (low/moderate/high/extreme)
  - [ ] Create wrapper script `scripts/calculate_risk.py`

### 3. Weather Integration
- [ ] **`get_current_weather_for_fire_risk(zone_bounds)`**
  - [ ] Create `alviaorange/weather.py` module
  - [ ] Integrate with weather APIs (OpenWeatherMap, NOAA)
  - [ ] Calculate Fire Weather Index (FWI) components
  - [ ] Create wrapper script `scripts/get_weather.py`

### 4. Enhanced Schema & Data Models
- [ ] **Expand Pydantic schemas in `alviaorange/schemas.py`**
  - [ ] Add `RiskAssessment` model
  - [ ] Add `WeatherData` model
  - [ ] Add `ZoneBounds` model
  - [ ] Add `FireWeatherIndex` model
  - [ ] Add comprehensive validation and error handling

---

## 🟡 HIGH PRIORITY - MVP Phase 2 (Should Have)

### 5. Fire Behavior Modeling
- [ ] **`predict_fire_spread(ignition_point, weather_conditions, fuel_model, time_hours)`**
  - [ ] Create `alviaorange/fire_behavior.py` module
  - [ ] Implement Rothermel fire spread model
  - [ ] Add fire intensity calculations
  - [ ] Create polygon generation for spread prediction

- [ ] **`calculate_fire_intensity(fuel_load, moisture_content, wind_speed, slope)`**
  - [ ] Implement flame length calculations
  - [ ] Add fire intensity classification

### 6. Fuel Analysis
- [ ] **`analyze_fuel_load(zone_bounds, satellite_date)`**
  - [ ] Create `alviaorange/fuel_analysis.py` module
  - [ ] Integrate with Landsat/Sentinel imagery
  - [ ] Implement fuel type classification (Anderson 13/Scott & Burgan 40)

- [ ] **`get_fuel_moisture_content(zone_bounds, date)`**
  - [ ] Calculate live and dead fuel moisture
  - [ ] Integrate with satellite-derived moisture indices

### 7. Weather Forecasting
- [ ] **`get_weather_forecast_for_fire_risk(zone_bounds, days)`**
  - [ ] Extend weather module for forecasting
  - [ ] Add multi-day fire weather predictions

---

## 🟢 MEDIUM PRIORITY - Post-MVP (Nice to Have)

### 8. Historical Analysis
- [ ] **`get_historical_fire_data(zone_bounds, years_back)`**
- [ ] **`analyze_fire_risk_trends(zone_bounds, period, years)`**
- [ ] **`calculate_burn_probability(zone_bounds, timeframe)`**

### 9. Satellite Data Integration
- [ ] **`detect_burn_scars(zone_bounds, start_date, end_date)`**
- [ ] **`get_vegetation_health_indices(zone_bounds, index_type, date)`**

### 10. Advanced Features
- [ ] **Alert system implementation**
- [ ] **Performance optimization**
- [ ] **Comprehensive testing suite**

---

## 🔧 Implementation Standards

### Function Signature Pattern
```python
def function_name(
    required_param: Type,
    optional_param: Type = default_value
) -> ReturnType:
    """Brief description with Args, Returns, and Raises sections."""
```

### Performance Requirements
- Hotspot detection: < 30 seconds for 100km² area
- Risk assessment: < 10 seconds
- Fire spread prediction: < 60 seconds for 24-hour simulation
- Weather data retrieval: < 5 seconds

### Error Handling Requirements
- Invalid coordinates/bounds validation
- Missing/corrupted satellite data handling
- API rate limits and network timeouts
- Invalid date ranges

---

## 📋 Current Status
- [x] Project structure established
- [x] Basic Pydantic schemas created
- [x] Example notebook created
- [ ] Core MVP functions implementation (IN PROGRESS) 