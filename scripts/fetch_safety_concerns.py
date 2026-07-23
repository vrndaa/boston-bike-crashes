"""
Build data/safety_concerns.geojson from the Vision Zero Safety Concerns
(Current) dataset.

Source CSV already present at src/vision_zero_safety_concerns__current.csv
(pulled in an earlier session) — verified against the live CKAN resource
before use (see fetch log): resource id 42c33f05-2572-404e-9782-38d755f0f069,
total=557, fields and first record match exactly. No re-download needed.

Saves the FULL dataset (all modes), not just bike concerns, with a `mode`
property so the app can filter client-side. Bike-only count is reported
here for confirmation but not used to drop rows.
"""

import csv
import json
from datetime import datetime
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "vision_zero_safety_concerns__current.csv"
OUT = Path(__file__).resolve().parent.parent / "data" / "safety_concerns.geojson"

MODE_MAP = {
    "bikes": "bike",
    "walks": "walk",
    "drives": "drive",
    "uses an assistive device": "assistive_device",
    "other": "other",
}


def parse_ts(raw):
    # Format observed: "6/14/2022 19:39:23.797" (no leading zeros)
    return datetime.strptime(raw, "%m/%d/%Y %H:%M:%S.%f")


def main():
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    missing_coords = 0
    features = []
    mode_counts = {}
    dates = []

    for row in rows:
        x, y = row["POINT_X"], row["POINT_Y"]
        if not x or not y:
            missing_coords += 1
            continue

        raw_mode = (row["your_mode_of_transportation"] or "").strip()
        mode = MODE_MAP.get(raw_mode, raw_mode or "unknown")
        mode_counts[mode] = mode_counts.get(mode, 0) + 1

        ts = None
        if row["date_and_time"]:
            dt = parse_ts(row["date_and_time"])
            dates.append(dt)
            ts = int(dt.timestamp() * 1000)

        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [float(x), float(y)]},
                "properties": {
                    "mode": mode,
                    "mode_raw": raw_mode,
                    "request": row["request"] or None,
                    "request_other": row["request_other"] or None,
                    "comments": row["additional_comments"] or None,
                    "timestamp_ms": ts,
                },
            }
        )

    geojson = {"type": "FeatureCollection", "features": features}
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(geojson, f)

    bike_count = mode_counts.get("bike", 0)
    print(f"Total records: {len(rows)}")
    print(f"Written features: {len(features)}")
    print(f"Bike-related (mode == 'bikes'): {bike_count}")
    print(f"Mode breakdown: {mode_counts}")
    print(f"Missing coordinates: {missing_coords}")
    if dates:
        print(f"Date range: {min(dates).date()} to {max(dates).date()}")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
