import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from alviaorange.hotspots import fetch_hotspots


def test_fetch_hotspots_default():
    assert fetch_hotspots() == ["AB-001", "BC-123"]
