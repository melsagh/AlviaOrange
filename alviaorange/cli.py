"""Command line interface for AlviaOrange."""

from __future__ import annotations

import argparse
from typing import Iterable

from .hotspots import fetch_hotspots


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Fetch wildfire hotspots")
    parser.add_argument(
        "--region",
        default="Canada",
        help="Region for which to fetch hotspots (default: Canada)",
    )
    args = parser.parse_args(argv)
    hotspots = fetch_hotspots(args.region)
    for hotspot in hotspots:
        print(hotspot)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
