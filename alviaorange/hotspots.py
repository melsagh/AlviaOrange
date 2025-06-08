"""Hotspot retrieval utilities with basic region and shapefile support."""

from __future__ import annotations

from typing import Dict, List, Union

from pathlib import Path

import shapefile  # type: ignore
from shapely.geometry import Polygon, shape
from shapely.ops import unary_union, transform
from pyproj import CRS, Transformer


# Simplistic polygon definitions for Canada and the USA. These are rough
# bounding boxes purely for demonstration purposes.
_CANADA_POLYGON = Polygon([(-141, 41), (-52, 41), (-52, 83), (-141, 83)])
_USA_POLYGON = Polygon([(-125, 24), (-66, 24), (-66, 49), (-125, 49)])

# Mapping of region name to polygon
REGION_SHAPES: Dict[str, Polygon] = {
    "Canada": _CANADA_POLYGON,
    "USA": _USA_POLYGON,
}


def _read_shapefile(path: Path) -> Polygon:
    """Return the union of all geometries in a shapefile in WGS84 coordinates."""

    reader = shapefile.Reader(str(path))
    geometries = [shape(s.__geo_interface__) for s in reader.shapes()]
    geom = unary_union(geometries)

    prj_file = path.with_suffix(".prj")
    if prj_file.exists():
        prj_txt = prj_file.read_text().strip()
        if prj_txt:
            try:
                src_crs = CRS.from_wkt(prj_txt)
            except Exception:
                try:
                    src_crs = CRS.from_user_input(prj_txt)
                except Exception:
                    src_crs = None
            if src_crs and src_crs != CRS.from_epsg(4326):
                transformer = Transformer.from_crs(src_crs, 4326, always_xy=True)
                geom = transform(transformer.transform, geom)

    return geom


def _fetch_by_region_name(name: str) -> List[str]:
    """Internal helper returning hotspot list for a named region."""

    sample_data = {
        "Canada": ["AB-001", "BC-123"],
        "USA": ["CA-999", "OR-456"],
    }
    return sample_data.get(name, [])


def fetch_hotspots(
    region: Union[str, Path] = "Canada",
) -> Union[List[str], Dict[str, List[str]]]:
    """Return hotspot identifiers for a region or regions defined by a shapefile."""

    path = Path(region)
    if path.exists() and path.suffix.lower() == ".shp":
        geom = _read_shapefile(path)
        results: Dict[str, List[str]] = {}
        for name, poly in REGION_SHAPES.items():
            if poly.intersects(geom):
                results[name] = _fetch_by_region_name(name)
        return results

    return _fetch_by_region_name(str(region))
