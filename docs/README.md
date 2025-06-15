# AlviaOrange Documentation

This directory contains the Sphinx-based documentation for AlviaOrange. The documentation is automatically built and deployed to GitHub Pages.

## 🏗️ Documentation Structure

```
docs/
├── conf.py                 # Sphinx configuration
├── index.rst              # Main documentation index
├── installation.rst       # Installation guide
├── quickstart.rst         # Quick start guide
├── api/                   # API reference documentation
│   ├── modules.rst        # Module overview
│   ├── hotspots.rst       # Hotspots module docs
│   └── schemas.rst        # Schemas module docs
├── _static/               # Static files (CSS, images)
│   └── custom.css         # Custom styling
├── _build/                # Built documentation (generated)
└── Makefile              # Build commands

```

## 🚀 Quick Start

### Prerequisites

Install documentation dependencies:

```bash
pip install -r requirements-dev.txt
```

### Building Documentation

Build HTML documentation:

```bash
cd docs
make html
```

Serve locally for development:

```bash
make serve
# Open http://localhost:8000 in your browser
```

### Live Development

For live reloading during development:

```bash
# Install sphinx-autobuild
pip install sphinx-autobuild

# Start live server
make livehtml
# Open http://localhost:8000 in your browser
```

## 📝 Writing Documentation

### Adding New Pages

1. Create a new `.rst` file in the appropriate directory
2. Add it to the relevant `toctree` in `index.rst` or other parent files
3. Use proper reStructuredText formatting

### API Documentation

API documentation is automatically generated from docstrings using Sphinx autodoc:

```python
def example_function(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2 with default value
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        
    Example:
        >>> result = example_function("test", 20)
        >>> print(result)
        {'status': 'success'}
    """
    pass
```

### Code Examples

Use code blocks with syntax highlighting:

```rst
.. code-block:: python

   from alviaorange.hotspots import detect_hotspots_for_zone
   
   result = detect_hotspots_for_zone(
       zone_bounds={'north': 50, 'south': 49, 'east': -120, 'west': -121},
       time_range={'start_date': '2024-01-01T00:00:00Z', 'end_date': '2024-01-02T00:00:00Z'}
   )
```

### Jupyter Notebooks

Jupyter notebooks in the `notebooks/` directory are automatically included:

1. Place notebooks in `../notebooks/`
2. Reference them in documentation:

```rst
.. toctree::
   :maxdepth: 2
   
   ../notebooks/01-data-scientist-workflow
```

## 🎨 Styling

### Custom CSS

Custom styling is defined in `_static/custom.css` with Alvia brand colors:

- Orange: `#FF6B35`
- Blue: `#2980B9`
- Dark: `#2C3E50`
- Light: `#ECF0F1`

### Theme Configuration

The documentation uses the Read the Docs theme with custom configuration in `conf.py`.

## 🔧 Build Commands

### Available Make Targets

```bash
# Basic commands
make html          # Build HTML documentation
make clean         # Clean build directory
make serve         # Serve built docs locally

# Development commands
make livehtml      # Live reload server
make clean-all     # Clean everything including generated files
make strict        # Build with warnings as errors
make linkcheck     # Check for broken links

# API documentation
make apidoc        # Generate API docs from source
make rebuild       # Full rebuild with API docs

# Quality checks
make coverage      # Check docstring coverage
```

### Manual Sphinx Commands

```bash
# Build HTML
sphinx-build -b html . _build/html

# Build with warnings as errors
sphinx-build -W -b html . _build/html

# Check links
sphinx-build -b linkcheck . _build/linkcheck

# Generate API docs
sphinx-apidoc -o api/ ../alviaorange/ --force --module-first
```

## 🚀 Deployment

### GitHub Pages (Automatic)

Documentation is automatically deployed to GitHub Pages via GitHub Actions:

1. Push changes to `main` branch
2. GitHub Actions builds documentation
3. Deploys to `https://your-username.github.io/AlviaOrange/`

### Manual Deployment

For manual deployment to other platforms:

```bash
# Build documentation
make html

# Deploy _build/html/ directory to your hosting platform
rsync -av _build/html/ user@server:/path/to/docs/
```

## 📊 Quality Checks

### Docstring Coverage

Check documentation coverage:

```bash
pip install interrogate
make coverage
```

Target: 80% docstring coverage

### Link Checking

Check for broken links:

```bash
make linkcheck
```

### Build Validation

Ensure documentation builds without warnings:

```bash
make strict
```

## 🔍 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure package is installed in development mode
pip install -e ..
```

**Missing Dependencies**
```bash
# Install all documentation dependencies
pip install -r requirements-dev.txt
```

**Build Failures**
```bash
# Clean and rebuild
make clean-all
make rebuild
```

**Broken Links**
```bash
# Check and fix broken links
make linkcheck
```

### Performance Issues

For large documentation builds:

```bash
# Parallel builds (if supported)
make html SPHINXOPTS="-j auto"

# Skip notebook execution
export NBSPHINX_EXECUTE=never
make html
```

## 📚 Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)
- [Sphinx AutoDoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html)
- [GitHub Pages](https://pages.github.com/)

## 🤝 Contributing

When contributing to documentation:

1. Follow the existing structure and style
2. Test builds locally before submitting
3. Ensure all links work
4. Add examples for new features
5. Update API documentation for code changes

For more details, see the main [Contributing Guide](../CONTRIBUTING.md). 