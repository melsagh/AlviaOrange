# AlviaOrange Python Library - Node.js Integration Guide

This guide explains how to integrate the AlviaOrange Python library with your Node.js/TypeScript API server.

## 🏗️ Architecture Overview

```
Frontend (React) → Node.js API → Python AlviaOrange → External Data Sources
                      ↓
                 PostgreSQL Database
```

The Python library provides core wildfire analysis functions that your Node.js API server calls via child processes using the `python-shell` library.

---

## 📦 Installation & Setup

### 1. Install Python Dependencies

```bash
# In the AlviaOrange directory
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies

```bash
# In your Node.js API project
npm install python-shell
npm install @types/python-shell  # For TypeScript
```

### 3. Environment Variables

Set these environment variables in your Node.js project:

```env
PYTHON_PATH=/path/to/python  # Path to Python executable
ALVIA_PYTHON_LIB_PATH=/path/to/AlviaOrange  # Path to AlviaOrange directory
NASA_FIRMS_API_KEY=your_nasa_firms_api_key  # Optional: for real satellite data
```

---

## 🔥 Critical Functions (MVP Phase 1)

### 1. Hotspot Detection

#### Function: `detect_hotspots_for_zone`
**Script:** `scripts/detect_hotspots.py`
**API Endpoint:** `GET /api/orange/hotspots`

**TypeScript Integration:**
```typescript
import { PythonShell } from 'python-shell';

interface HotspotDetectionParams {
  north: number;
  south: number;
  east: number;
  west: number;
  start_date: string;  // ISO format with Z
  end_date: string;    // ISO format with Z
  sources?: string[];  // Default: ["VIIRS", "MODIS", "FIRMS"]
  min_confidence?: number;  // Default: 70
  api_key?: string;
}

interface HotspotResult {
  success: boolean;
  hotspots: Array<{
    id: string;
    latitude: number;
    longitude: number;
    timestamp: string;
    confidence: number;
    frp: number;  // Fire Radiative Power in MW
    source: string;
    metadata: {
      satellite: string;
      scan_angle: number;
      pixel_size: number;
      brightness_temp: number;
    };
  }>;
  total_count: number;
  query_time: string;
  error?: string;
}

async function detectHotspots(params: HotspotDetectionParams): Promise<HotspotResult> {
  return new Promise((resolve, reject) => {
    const args = [
      params.north.toString(),
      params.south.toString(),
      params.east.toString(),
      params.west.toString(),
      params.start_date,
      params.end_date,
      (params.sources || ["VIIRS", "MODIS", "FIRMS"]).join(','),
      (params.min_confidence || 70).toString(),
      params.api_key || ''
    ];

    const options = {
      mode: 'text' as const,
      pythonPath: process.env.PYTHON_PATH,
      scriptPath: `${process.env.ALVIA_PYTHON_LIB_PATH}/scripts`,
      args: args
    };

    PythonShell.run('detect_hotspots.py', options, (err, results) => {
      if (err) {
        reject(new Error(`Python script error: ${err.message}`));
        return;
      }

      try {
        const result = JSON.parse(results![0]) as HotspotResult;
        resolve(result);
      } catch (parseErr) {
        reject(new Error(`Failed to parse Python output: ${parseErr}`));
      }
    });
  });
}

// Usage in your API route
app.get('/api/orange/hotspots', async (req, res) => {
  try {
    const { north, south, east, west, start_date, end_date, sources, min_confidence } = req.query;
    
    const result = await detectHotspots({
      north: parseFloat(north as string),
      south: parseFloat(south as string),
      east: parseFloat(east as string),
      west: parseFloat(west as string),
      start_date: start_date as string,
      end_date: end_date as string,
      sources: sources ? (sources as string).split(',') : undefined,
      min_confidence: min_confidence ? parseInt(min_confidence as string) : undefined
    });

    if (!result.success) {
      return res.status(400).json({ error: result.error });
    }

    // Store in database if needed
    // await storeHotspotsInDB(result.hotspots);

    res.json(result);
  } catch (error) {
    console.error('Hotspot detection error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

#### Function: `get_active_hotspots`
**Script:** `scripts/get_active_hotspots.py`
**API Endpoint:** `GET /api/orange/hotspots/active`

**Command-line usage:**
```bash
python get_active_hotspots.py <north> <south> <east> <west> [hours_back] [min_confidence]
```

### 2. Risk Assessment

#### Function: `calculate_fire_risk_score`
**Script:** `scripts/calculate_risk.py`
**API Endpoint:** `POST /api/orange/risk-assessments/calculate`

**TypeScript Integration:**
```typescript
interface RiskAssessmentParams {
  zone_data: {
    bounds: {
      north: number;
      south: number;
      east: number;
      west: number;
    };
    area_km2: number;
  };
  weather_data: {
    temperature: number;
    humidity: number;
    wind_speed: number;
    wind_direction: number;
    precipitation: number;
    timestamp: string;
  };
  vegetation_data: {
    ndvi?: number;
    moisture_content?: number;
    fuel_load?: number;
  };
  topography_data?: {
    elevation?: number;
    slope?: number;
    aspect?: number;
  };
}

interface RiskAssessmentResult {
  success: boolean;
  risk_score: number;  // 0-100
  risk_level: 'low' | 'moderate' | 'high' | 'extreme';
  weather_risk: 'low' | 'moderate' | 'high' | 'extreme';
  vegetation_dryness: 'low' | 'moderate' | 'high' | 'severe';
  factors: {
    temperature_factor: number;
    humidity_factor: number;
    wind_factor: number;
    fuel_moisture_factor: number;
    drought_index: number;
    slope_factor?: number;
  };
  recommendations: string[];
  error?: string;
}

async function calculateRiskScore(params: RiskAssessmentParams): Promise<RiskAssessmentResult> {
  return new Promise((resolve, reject) => {
    const args = [
      JSON.stringify(params.zone_data),
      JSON.stringify(params.weather_data),
      JSON.stringify(params.vegetation_data),
      params.topography_data ? JSON.stringify(params.topography_data) : ''
    ];

    const options = {
      mode: 'text' as const,
      pythonPath: process.env.PYTHON_PATH,
      scriptPath: `${process.env.ALVIA_PYTHON_LIB_PATH}/scripts`,
      args: args
    };

    PythonShell.run('calculate_risk.py', options, (err, results) => {
      if (err) {
        reject(new Error(`Python script error: ${err.message}`));
        return;
      }

      try {
        const result = JSON.parse(results![0]) as RiskAssessmentResult;
        resolve(result);
      } catch (parseErr) {
        reject(new Error(`Failed to parse Python output: ${parseErr}`));
      }
    });
  });
}

// Usage in your API route
app.post('/api/orange/risk-assessments/calculate', async (req, res) => {
  try {
    const result = await calculateRiskScore(req.body);

    if (!result.success) {
      return res.status(400).json({ error: result.error });
    }

    // Store in database
    // await storeRiskAssessmentInDB(result);

    res.json(result);
  } catch (error) {
    console.error('Risk assessment error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

---

## 🔧 Error Handling Best Practices

### 1. Python Script Error Handling

```typescript
interface PythonError {
  success: false;
  error: string;
  details?: any;
}

function isPythonError(result: any): result is PythonError {
  return result && result.success === false && result.error;
}

async function callPythonScript<T>(
  scriptName: string, 
  args: string[]
): Promise<T> {
  return new Promise((resolve, reject) => {
    const options = {
      mode: 'text' as const,
      pythonPath: process.env.PYTHON_PATH,
      scriptPath: `${process.env.ALVIA_PYTHON_LIB_PATH}/scripts`,
      args: args
    };

    PythonShell.run(scriptName, options, (err, results) => {
      if (err) {
        reject(new Error(`Python execution error: ${err.message}`));
        return;
      }

      if (!results || results.length === 0) {
        reject(new Error('No output from Python script'));
        return;
      }

      try {
        const result = JSON.parse(results[0]);
        
        if (isPythonError(result)) {
          reject(new Error(`Python script error: ${result.error}`));
          return;
        }

        resolve(result as T);
      } catch (parseErr) {
        reject(new Error(`Failed to parse Python output: ${parseErr}`));
      }
    });
  });
}
```

### 2. Timeout Handling

```typescript
function withTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) => 
      setTimeout(() => reject(new Error('Operation timed out')), timeoutMs)
    )
  ]);
}

// Usage
const result = await withTimeout(
  detectHotspots(params), 
  30000  // 30 second timeout
);
```

---

## 📊 Database Integration

### Storing Results in PostgreSQL

```typescript
// Example with Drizzle ORM
import { db } from './db';
import { hotspots, riskAssessments } from './db/schema';

async function storeHotspotsInDB(hotspotsData: any[], zoneId: string) {
  const hotspotsToInsert = hotspotsData.map(hotspot => ({
    id: hotspot.id,
    zoneId: zoneId,
    latitude: hotspot.latitude,
    longitude: hotspot.longitude,
    timestamp: new Date(hotspot.timestamp),
    confidence: hotspot.confidence,
    frp: hotspot.frp,
    source: hotspot.source,
    metadata: hotspot.metadata,
    createdAt: new Date()
  }));

  await db.insert(hotspots).values(hotspotsToInsert);
}

async function storeRiskAssessmentInDB(riskData: RiskAssessmentResult, zoneId: string) {
  await db.insert(riskAssessments).values({
    id: crypto.randomUUID(),
    zoneId: zoneId,
    timestamp: new Date(),
    riskScore: riskData.risk_score,
    riskLevel: riskData.risk_level,
    weatherRisk: riskData.weather_risk,
    vegetationDryness: riskData.vegetation_dryness,
    factors: riskData.factors,
    createdAt: new Date()
  });
}
```

---

## 🚀 Performance Optimization

### 1. Caching Results

```typescript
import NodeCache from 'node-cache';

const cache = new NodeCache({ stdTTL: 300 }); // 5 minute cache

async function getCachedHotspots(params: HotspotDetectionParams): Promise<HotspotResult> {
  const cacheKey = `hotspots:${JSON.stringify(params)}`;
  const cached = cache.get<HotspotResult>(cacheKey);
  
  if (cached) {
    return cached;
  }

  const result = await detectHotspots(params);
  cache.set(cacheKey, result);
  
  return result;
}
```

### 2. Parallel Processing

```typescript
async function getComprehensiveFireData(zoneParams: any) {
  const [hotspots, riskAssessment] = await Promise.all([
    detectHotspots(zoneParams),
    calculateRiskScore(zoneParams)
  ]);

  return {
    hotspots,
    riskAssessment,
    timestamp: new Date().toISOString()
  };
}
```

---

## 🧪 Testing

### Unit Tests

```typescript
import { describe, it, expect } from 'vitest';

describe('AlviaOrange Integration', () => {
  it('should detect hotspots successfully', async () => {
    const params = {
      north: 50,
      south: 49,
      east: -120,
      west: -121,
      start_date: '2024-01-01T00:00:00Z',
      end_date: '2024-01-02T00:00:00Z'
    };

    const result = await detectHotspots(params);
    
    expect(result.success).toBe(true);
    expect(result.total_count).toBeGreaterThanOrEqual(0);
    expect(Array.isArray(result.hotspots)).toBe(true);
  });

  it('should calculate risk assessment successfully', async () => {
    const params = {
      zone_data: {
        bounds: { north: 50, south: 49, east: -120, west: -121 },
        area_km2: 100
      },
      weather_data: {
        temperature: 35,
        humidity: 15,
        wind_speed: 25,
        wind_direction: 225,
        precipitation: 0,
        timestamp: '2024-01-01T12:00:00Z'
      },
      vegetation_data: {
        moisture_content: 8
      }
    };

    const result = await calculateRiskScore(params);
    
    expect(result.success).toBe(true);
    expect(result.risk_score).toBeGreaterThanOrEqual(0);
    expect(result.risk_score).toBeLessThanOrEqual(100);
    expect(['low', 'moderate', 'high', 'extreme']).toContain(result.risk_level);
  });
});
```

---

## 📋 Available Scripts

| Script | Purpose | Command Line Args |
|--------|---------|-------------------|
| `detect_hotspots.py` | Detect hotspots in zone | `north south east west start_date end_date [sources] [min_confidence] [api_key]` |
| `get_active_hotspots.py` | Get active hotspots | `north south east west [hours_back] [min_confidence] [api_key]` |
| `calculate_risk.py` | Calculate fire risk | `zone_data_json weather_data_json vegetation_data_json [topography_data_json]` |

---

## 🔍 Troubleshooting

### Common Issues

1. **Python Path Issues**
   ```bash
   # Find Python path
   which python3
   # or
   where python
   ```

2. **Module Import Errors**
   - Ensure `ALVIA_PYTHON_LIB_PATH` is set correctly
   - Check that `requirements.txt` dependencies are installed

3. **JSON Parsing Errors**
   - Check that Python scripts output valid JSON
   - Ensure proper error handling in Python scripts

4. **Performance Issues**
   - Implement caching for frequently requested data
   - Use timeouts to prevent hanging requests
   - Consider background job processing for heavy operations

---

## 📞 Support

For integration support, check:
1. Python script outputs for error messages
2. Node.js console logs for detailed error information
3. Ensure all environment variables are properly set
4. Verify Python dependencies are installed correctly

The Python library is designed to be robust and provide detailed error messages to help with debugging integration issues. 