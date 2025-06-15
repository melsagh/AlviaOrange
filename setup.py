#!/usr/bin/env python3
"""
Setup script for AlviaOrange - Open-source wildfire detection and risk assessment library.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "AlviaOrange - Open-source wildfire detection and risk assessment library"

# Read requirements
def read_requirements(filename):
    req_path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="alviaorange",
    version="1.0.0",
    author="Alvia Platform Team",
    author_email="team@alvia.com",
    description="Open-source wildfire detection and risk assessment library",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/AlviaOrange",
    project_urls={
        "Bug Tracker": "https://github.com/your-username/AlviaOrange/issues",
        "Documentation": "https://your-username.github.io/AlviaOrange/",
        "Source Code": "https://github.com/your-username/AlviaOrange",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.24.0",
            "myst-parser>=2.0.0",
            "sphinx-copybutton>=0.5.2",
            "nbsphinx>=0.9.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
        ],
        "performance": [
            "numba>=0.58.0",
            "orjson>=3.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "alvia-detect-hotspots=scripts.detect_hotspots:main",
            "alvia-calculate-risk=scripts.calculate_risk:main",
        ],
    },
    include_package_data=True,
    package_data={
        "alviaorange": ["py.typed"],
    },
    keywords=[
        "wildfire",
        "fire detection",
        "risk assessment",
        "satellite data",
        "geospatial",
        "environmental monitoring",
        "climate",
        "disaster management",
    ],
    zip_safe=False,
) 