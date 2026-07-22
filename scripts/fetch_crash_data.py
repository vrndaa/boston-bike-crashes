"""
Pull Boston Vision Zero bike-crash records via the CKAN API, filter to
mode_type == 'bike', and export a GeoJSON with a timestamp_ms property
(so the MapLibre filter in CrashMap.svelte can compare against it directly).

See CLAUDE.md for the verified endpoint/schema details.

Usage:
    pip install pandas requests --break-system-packages
    python scripts/fetch_crash_data.py
"""

import json
import sys
from pathlib import Path

import pandas as pd
import requests

CSV_URL = (
    "https://data.boston.gov/datastore/dump/"
    "e4bfe397-6bfc-49c5-9367-c879fac7401d?bom=True"
)
OUTPUT = Path("data/boston_bike_crashes.geojson")


def main():
    print(f"Fetching {CSV_URL} ...")
    resp = requests.get(CSV_URL, timeout=60)
    resp.raise_for_status()

    from io import StringIO

    df = pd.read_csv(StringIO(resp.text))
    print(f"Total rows (all modes): {len(df)}")

    bike = df[df["mode_type"] == "bike"].copy()
    print(f"Bike rows: {len(bike)}")

    if len(bike) == 0:
        print("ERROR: zero bike rows found — check the mode_type filter/schema.")
        sys.exit(1)

    bike = bike.dropna(subset=["lat", "long", "dispatch_ts"])
    print(f"Bike rows with valid lat/long/timestamp: {len(bike)}")

    bike["dispatch_dt"] = pd.to_datetime(bike["dispatch_ts"], utc=True, errors="coerce")
    bike = bike.dropna(subset=["dispatch_dt"])

    print(f"Date range: {bike['dispatch_dt'].min()} to {bike['dispatch_dt'].max()}")

    features = []
    for _, row in bike.iterrows():
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row["long"]), float(row["lat"])],
                },
                "properties": {
                    "street": row.get("street"),
                    "location_type": row.get("location_type"),
                    "dispatch_ts": row["dispatch_dt"].isoformat(),
                    "timestamp_ms": int(row["dispatch_dt"].timestamp() * 1000),
                },
            }
        )

    geojson = {"type": "FeatureCollection", "features": features}

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(geojson))
    print(f"Wrote {OUTPUT} with {len(features)} features.")


if __name__ == "__main__":
    main()
