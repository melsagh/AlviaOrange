# AlviaOrange

AlviaOrange is an open-source collection of wildfire analytics and simulation tools.
The goal is to make it easy for data scientists to experiment with algorithms and
for developers to integrate them into larger systems such as the AlviaPlatform.

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd AlviaOrange

# Create a virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

## Running the example notebook

Install the optional Jupyter dependencies and start the notebook server:

```bash
pip install jupyter
jupyter notebook notebooks/example.ipynb
```

Additional notebooks demonstrating every feature with Plotly visualizations can
be found in the `notebooks/` directory. There is one notebook for each public
function so you can run them individually and explore the outputs
interactively.

### Displaying Fire Danger WMS tiles

The `fire_danger_wms_tile_url(date)` helper returns a WMS tile URL for the
Canadian Wildland Fire Information System (CWFIS). It can be used to display the
Fire Danger Rating layer on interactive maps. The example notebooks demonstrate
this with Plotly:

```python
from alviaorange import fire_danger_wms_tile_url
import plotly.graph_objects as go

token = "YOUR_MAPBOX_ACCESS_TOKEN"
tile_url = fire_danger_wms_tile_url("20230401")

fig = go.Figure(go.Scattermapbox())
fig.update_layout(
    mapbox=dict(
        accesstoken=token,
        style="open-street-map",
        layers=[dict(sourcetype="raster", source=[tile_url], below="traces")],
    ),
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)
fig.show()
```

## Node.js/TypeScript integration

Developers can interface with the Python tools using a CLI script or by exposing an
HTTP endpoint with frameworks like Flask or FastAPI. The CLI approach allows calling
Python scripts from Node.js using `child_process`. For more advanced use cases,
consider running a lightweight HTTP server to expose endpoints for hotspot
retrieval or simulation.

## Using the CLI

Invoke the command line interface to print hotspots:

```bash
python -m alviaorange.cli --region Canada
```

Shapefiles can also be supplied instead of a region name. When the provided
polygon spans multiple supported regions, hotspots for each region will be
printed with the region name prefix.

If the shapefile includes a `.prj` file, its geometry will be reprojected to
WGS84 so that the coordinates match the simple polygons used in this example.
Otherwise the coordinates are assumed to already be in longitude/latitude.

```bash
python -m alviaorange.cli --region path/to/area.shp
```

## Air Quality Retrieval

The package also includes a function to fetch Canadian Air Quality data from
Environment Canada's website. Usage example:

```python
from alviaorange import fetch_air_quality

data = fetch_air_quality()
print(data.get("Toronto"))
```

Additional helpers are available. Historical data can be fetched for a
specific date or a range:

```python
from alviaorange import fetch_aqi_scale, fetch_air_quality_history

scale = fetch_aqi_scale()
history = fetch_air_quality_history("Toronto", "2024-01-01", "2024-01-02")
```

## Starting the HTTP server

An HTTP endpoint can be started with:

```bash
python scripts/run_server.py
```

This exposes `/hotspots?region=Canada` which returns a JSON list of hotspots.

## Packaging and Distribution

The project uses a `pyproject.toml` file for packaging. Once stable, the package can
be published to PyPI so other projects (like AlviaPlatform) can install it as a
standard dependency.

To build and install locally:

```bash
pip install build
python -m build
pip install dist/alviaorange-*.whl
```

## Contributing Notebooks or Algorithms

Place new notebooks in the `notebooks/` directory and keep algorithm modules inside
`alviaorange/`. Ensure that any new functionality includes corresponding tests in
`tests/`. Follow PEP 8 style and include type hints where practical.

## 📚 Documentation

### Online Documentation

Visit our comprehensive documentation site: **[AlviaOrange Documentation](https://your-username.github.io/AlviaOrange/)**

The documentation includes:
- 🚀 **Quick Start Guide** - Get up and running in minutes
- 📖 **Installation Guide** - Detailed setup instructions
- 🔧 **API Reference** - Complete function documentation
- 📓 **Examples** - Jupyter notebooks and code samples
- 🤝 **Contributing Guide** - How to contribute to the project

### Building Documentation Locally

To build and view the documentation locally:

```bash
# Install documentation dependencies
pip install -r requirements-dev.txt

# Build the documentation
cd docs
sphinx-build -b html . _build/html

# Serve locally
python -m http.server 8000 -d _build/html
# Open http://localhost:8000 in your browser
```

### Documentation Features

- **Auto-generated API docs** from docstrings using Sphinx
- **Professional styling** with Read the Docs theme and custom Alvia branding
- **Interactive examples** with copy-paste code blocks
- **Jupyter notebook integration** for data science workflows
- **GitHub Pages deployment** for easy access
- **Search functionality** across all documentation
- **Mobile-responsive design** for any device

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
