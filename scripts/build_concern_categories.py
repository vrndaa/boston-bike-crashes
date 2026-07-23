"""
Build the bike-only safety-concern category breakdown for the Layer 2 bar
chart, using the dataset's own field domain (not guessed labels).

Domain source: the Survey123 FeatureServer backing this dataset publishes
a codedValue domain on the `request` field — pulled live from
https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/services/
survey123_9c1eb48670794d348ba0f99e1d942028/FeatureServer/0?f=json
(resource listed as "ArcGIS GeoServices REST API" on the dataset's
data.boston.gov page). Domain 'name' values are the official label text;
this script only lightly cleans them for chart display (capitalization,
punctuation), it does not invent categories.
"""

import json
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "safety_concerns.geojson"
OUT_JSON = Path(__file__).resolve().parent.parent / "data" / "concern_categories_bike.json"

# Pulled verbatim from the FeatureServer's codedValue domain on `request`
# (see docstring). code -> official domain name.
OFFICIAL_DOMAIN = {
    "bikefacility": "bike facilities don't exist or need improvement",
    "visibility": "it’s hard to see / low visibility",
    "request": "request something that is not listed here",  # unused code, not present in data
    "yieldgoing": "people don't yield while going straight",
    "yieldturn": "people don't yield while turning",
    "doublepark": "people double park their vehicles",
    "runlightssigns": "people run red lights / stop signs",
    "speeding": "people speed",
    "sidewalk": "sidewalks/ramps don't exist or need improvement",
    "walksignal": 'the wait for the "Walk" signal is too long',
    "other": "Other",
    "notenoughtime": "people are not given enough time to cross the street",
    "toomanylanes": "people have to cross too many lanes / too far",
    "awayfromside": "people cross away from the sidewalks",
    "roadwaymaint": "roadway surface needs maintenance",
}

# Chart-display labels: official domain text cleaned to a short noun
# phrase, consistent style with the rest of the app's UI copy. Kept as a
# visible mapping (not hidden inside a formatter) so it's easy to compare
# against OFFICIAL_DOMAIN above.
DISPLAY_LABELS = {
    "bikefacility": "Bike facilities missing or inadequate",
    "yieldturn": "Failure to yield (turning)",
    "other": "Other",
    "doublepark": "Double parking",
    "runlightssigns": "Running red lights / stop signs",
    "roadwaymaint": "Roadway surface needs maintenance",
    "yieldgoing": "Failure to yield (going straight)",
    "speeding": "Speeding",
    "sidewalk": "Sidewalks/ramps missing or inadequate",
    "visibility": "Low visibility",
    "walksignal": "Walk signal wait too long",
    "awayfromside": "People crossing away from the sidewalk",
    "notenoughtime": "Not enough time to cross",
    "toomanylanes": "Too many lanes / too far to cross",
}


def main():
    geojson = json.loads(DATA.read_text())
    bike = [f["properties"] for f in geojson["features"] if f["properties"]["mode"] == "bike"]
    assert len(bike) == 176, f"expected 176 bike rows, got {len(bike)}"

    counts = Counter(p["request"] for p in bike)

    breakdown = [
        {"code": code, "category": DISPLAY_LABELS[code], "count": count}
        for code, count in counts.most_common()
    ]

    OUT_JSON.write_text(json.dumps(breakdown, indent=2))

    print("=== Final bike-only concern-category breakdown ===")
    for row in breakdown:
        print(f"{row['count']:>4}  {row['category']}  ({row['code']})")
    print()
    print("Total:", sum(r["count"] for r in breakdown))
    print("Wrote", OUT_JSON)


if __name__ == "__main__":
    main()
