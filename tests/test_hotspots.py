import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from alviaorange.hotspots import fetch_hotspots


def test_fetch_hotspots_default():
    assert fetch_hotspots() == ["AB-001", "BC-123"]


def test_fetch_hotspots_shapefile(tmp_path):
    import shapefile

    shp_path = tmp_path / "area"
    w = shapefile.Writer(str(shp_path))
    w.field("name", "C")
    # Polygon that spans southern Canada and northern USA
    w.poly(
        [
            [
                (-110, 45),
                (-90, 45),
                (-90, 55),
                (-110, 55),
                (-110, 45),
            ]
        ]
    )
    w.record("test")
    w.close()

    result = fetch_hotspots(shp_path.with_suffix(".shp"))
    assert isinstance(result, dict)
    assert "Canada" in result
    assert "USA" in result


def test_fetch_hotspots_shapefile_projected(tmp_path):
    import shapefile
    import pyproj

    shp_path = tmp_path / "area"
    w = shapefile.Writer(str(shp_path))
    w.field("name", "C")
    transformer = pyproj.Transformer.from_crs(4326, 3857, always_xy=True)
    ring = [
        (-110, 45),
        (-90, 45),
        (-90, 55),
        (-110, 55),
        (-110, 45),
    ]
    w.poly([[transformer.transform(x, y) for x, y in ring]])
    w.record("test")
    w.close()
    (tmp_path / "area.prj").write_text(pyproj.CRS.from_epsg(3857).to_wkt())

    result = fetch_hotspots(shp_path.with_suffix(".shp"))
    assert isinstance(result, dict)
    assert "Canada" in result
    assert "USA" in result
