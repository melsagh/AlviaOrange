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
