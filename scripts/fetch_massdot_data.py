"""
Pull Boston bicycle crash records from MassDOT's per-year IMPACT FeatureServers,
for the years that actually exist on the endpoint (2021-2025; 2019/2020 have no
FeatureServer here, confirmed by querying the service listing directly).

See CLAUDE.md for the verified endpoint/schema details, and the project owner's
2026-07-22 decision to narrow scope to 2021-2025 after 2019/2020 came back 404/500.

Usage:
    python scripts/fetch_massdot_data.py
"""

import csv
import sys
import time
from pathlib import Path

import requests

BASE = "https://gis.crashdata.dot.mass.gov/arcgis/rest/services/MassDOT"
YEARS = [2021, 2022, 2023, 2024, 2025]
YEAR_SUFFIX = {2023: "v"}  # MASSDOT_ODP_OPEN_2023v

WHERE = "CITY_TOWN_NAME = 'BOSTON' AND NON_MTRST_TYPE_CL LIKE '%Bicycl%'"
OUT_FIELDS = (
    "CRASH_NUMB,CRASH_DATETIME,CRASH_DATE_TEXT,CRASH_TIME_2,CRASH_SEVERITY_DESCR,"
    "NUMB_FATAL_INJR,NUMB_NONFATAL_INJR,RDWY,NEAR_INT_RDWY,NON_MTRST_TYPE_CL,"
    "WEATH_COND_DESCR,AMBNT_LIGHT_DESCR,MAX_INJR_SVRTY_CL"
)
OUTPUT = Path("data/massdot_boston_bike_crashes.csv")
PAGE_SIZE = 1000


def fetch_year(year):
    service = f"MASSDOT_ODP_OPEN_{year}{YEAR_SUFFIX.get(year, '')}"
    url = f"{BASE}/{service}/FeatureServer/0/query"

    all_features = []
    offset = 0
    while True:
        params = {
            "where": WHERE,
            "outFields": OUT_FIELDS,
            "outSR": "4326",
            "f": "json",
            "returnGeometry": "true",
            "resultOffset": offset,
            "resultRecordCount": PAGE_SIZE,
        }
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if "error" in data:
            raise RuntimeError(f"{year}: API error: {data['error']}")

        feats = data.get("features", [])
        all_features.extend(feats)

        if data.get("exceededTransferLimit") and feats:
            offset += len(feats)
            time.sleep(0.2)
            continue
        break

    return all_features


def main():
    rows = []
    field_names = [f.strip() for f in OUT_FIELDS.split(",")] + ["lon", "lat", "source_year"]

    for year in YEARS:
        try:
            feats = fetch_year(year)
        except Exception as exc:
            print(f"{year}: ERROR - {exc}")
            sys.exit(1)

        print(f"{year}: {len(feats)} Boston bike crashes")

        for feat in feats:
            attrs = feat.get("attributes", {})
            geom = feat.get("geometry") or {}
            row = {k: attrs.get(k) for k in field_names if k in attrs}
            row["lon"] = geom.get("x")
            row["lat"] = geom.get("y")
            row["source_year"] = year
            rows.append(row)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nTotal: {len(rows)} rows written to {OUTPUT}")


if __name__ == "__main__":
    main()
