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

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
