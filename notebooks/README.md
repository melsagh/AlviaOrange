# AlviaOrange Notebooks

This directory contains Jupyter notebooks for testing, demonstration, and analysis of the AlviaOrange wildfire monitoring API.

## 📓 Available Notebooks

### `comprehensive_api_testing.ipynb`
**Comprehensive API Testing & Validation**

A complete testing suite for all AlviaOrange API v2.1.0 endpoints.

#### 🎯 **Purpose**
- Validate all API endpoints are working correctly
- Demonstrate API usage with real examples
- Analyze response times and performance
- Verify authentication and error handling
- Generate visual summaries of test results

#### 🧪 **Test Coverage**
- **System Health** - Service status monitoring
- **Hotspot Detection** - Enhanced spatial hotspot queries
- **Air Quality** - Historical data and scale definitions
- **Weather Services** - Forecasts and fire weather indices
- **Fire Danger Assessment** - Risk analysis and rating grids
- **Climate Data** - Weather stations and normals
- **Geospatial Services** - WMS tiles and capabilities
- **Zone Services** - Zone-specific risk assessment
- **Legacy Endpoints** - Backward compatibility testing
- **Authentication** - Security validation

#### 🚀 **How to Use**

1. **Start the AlviaOrange Server**
   ```bash
   # In the project root directory
   python scripts/run_server.py
   ```

2. **Launch Jupyter**
   ```bash
   # Install Jupyter if not already installed
   pip install jupyter
   
   # Start Jupyter in the project directory
   jupyter notebook
   ```

3. **Open the Notebook**
   - Navigate to `notebooks/comprehensive_api_testing.ipynb`
   - Click to open the notebook

4. **Run the Tests**
   - Click "Cell" → "Run All" to execute all tests
   - Or run cells individually to see detailed results
   - The notebook will automatically test server connectivity

#### 📊 **What You'll See**

The notebook provides:
- **Real-time testing** of all API endpoints
- **Detailed response analysis** with JSON examples
- **Performance metrics** including response times
- **Visual charts** showing success rates and performance
- **Error handling validation** for security
- **Summary tables** categorizing test results

#### 🔧 **Configuration**

The notebook is pre-configured with:
- **API Base URL**: `http://localhost:8001`
- **API Key**: `demo-key` (for development)
- **Test Coordinates**: Toronto, Vancouver, Calgary
- **Test Zone ID**: Pre-configured UUID for zone testing

To customize for your environment:
```python
# Modify these variables in the setup cell
API_BASE_URL = "http://your-server:port"
API_KEY = "your-api-key"
```

#### 📈 **Expected Results**

A successful run should show:
- **25+ endpoint tests** all passing
- **Response times** under 2 seconds
- **Authentication** working correctly
- **Error handling** rejecting invalid requests
- **Visual summary** with 100% success rate

#### 🐛 **Troubleshooting**

**Server Connection Issues:**
- Ensure the server is running: `python scripts/run_server.py`
- Check the server is on port 8001
- Verify no firewall blocking localhost:8001

**Authentication Failures:**
- Confirm you're using a valid API key
- Check the `VALID_API_KEYS` environment variable

**Import Errors:**
- Install missing packages: `pip install -r requirements.txt`
- Ensure you're in the correct Python environment

#### 🎨 **Visualizations**

The notebook generates several charts:
- **Success Rate Pie Chart** - Overall test results
- **Response Time Histogram** - Performance distribution
- **Category Success Rates** - Results by endpoint category
- **Slowest Endpoints** - Performance analysis

## 🔄 **Other Notebooks**

Additional notebooks in this directory provide specific functionality demonstrations:

- `01-data-scientist-workflow.ipynb` - Data science workflow examples
- `air_quality.ipynb` - Air quality analysis examples
- `hotspots.ipynb` - Hotspot detection demonstrations
- `weather_stations_demo.ipynb` - Weather station functionality
- `cwfis.ipynb` - CWFIS fire weather examples

## 📚 **Resources**

- **API Documentation**: `docs/API_GUIDE.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Interactive API Docs**: `http://localhost:8001/api/orange/docs`
- **Test Script**: `scripts/test_api.py`

## 🎯 **Next Steps**

After running the comprehensive test notebook:

1. **Review Results** - Check all tests passed
2. **Analyze Performance** - Review response times
3. **Customize Tests** - Add your specific use cases
4. **Integration** - Use examples for your application
5. **Production** - Configure production API keys

The comprehensive testing notebook is your gateway to understanding and validating the full AlviaOrange API capabilities! 🔥 