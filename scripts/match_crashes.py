"""
Match MassDOT Boston bicycle crashes (2021-2025) against Vision Zero bike
crashes and produce an enriched GeoJSON with provenance tags.

MassDOT's CRASH_DATETIME is returned as an epoch-ms field that, when read as
naive UTC, reproduces the local Eastern wall-clock time exactly (verified
against CRASH_TIME_2 on multiple rows) - i.e. it's local time mislabeled as
UTC. It must be localized to America/New_York and converted to true UTC
before comparing to Vision Zero's already-UTC dispatch_ts.

See CLAUDE.md and the project owner's 2026-07-22 decisions:
- match window: +/-2 hours and <100m haversine
- VZ crashes before 2021-01-01, and all of 2026, get provenance "pre_massdot"
  (MassDOT coverage here is 2021-2025 only)

Usage:
    python scripts/match_crashes.py
"""

import json
import math
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

MASSDOT_CSV = Path("data/massdot_boston_bike_crashes.csv")
VZ_GEOJSON = Path("data/boston_bike_crashes.geojson")
OUTPUT = Path("data/boston_bike_crashes_enriched.geojson")

EASTERN = ZoneInfo("America/New_York")
MATCH_HOURS = 2
MATCH_METERS = 100
EARTH_RADIUS_M = 6371000


def haversine_m(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def load_massdot():
    df = pd.read_csv(MASSDOT_CSV)
    # epoch ms, naive-UTC-labeled but actually local Eastern wall time
    local_naive = pd.to_datetime(df["CRASH_DATETIME"], unit="ms", utc=False)
    local_aware = local_naive.dt.tz_localize(EASTERN, ambiguous="NaT", nonexistent="NaT")
    df["dt_utc"] = local_aware.dt.tz_convert("UTC")
    df = df.dropna(subset=["dt_utc", "lat", "lon"]).reset_index(drop=True)
    return df


def load_vz():
    gj = json.loads(VZ_GEOJSON.read_text())
    rows = []
    for feat in gj["features"]:
        props = feat["properties"]
        lon, lat = feat["geometry"]["coordinates"]
        rows.append(
            {
                "dt_utc": pd.to_datetime(props["dispatch_ts"], utc=True),
                "lat": lat,
                "lon": lon,
                "props": props,
            }
        )
    return pd.DataFrame(rows)


def main():
    massdot = load_massdot()
    vz = load_vz()

    print(f"MassDOT rows loaded: {len(massdot)}")
    print(f"VZ rows loaded: {len(vz)}")

    is_pre = (vz.dt_utc < pd.Timestamp("2021-01-01", tz="UTC")) | (
        vz.dt_utc.dt.year == 2026
    )
    vz_attempt = vz[~is_pre].copy().reset_index(drop=True)
    vz_pre = vz[is_pre].copy().reset_index(drop=True)

    print(f"VZ crashes eligible for matching (2021-2025): {len(vz_attempt)}")
    print(f"VZ crashes set to pre_massdot (pre-2021 or 2026): {len(vz_pre)}")

    # candidate pairs: vectorized haversine + time diff, brute force
    vz_times = vz_attempt.dt_utc.values.astype("datetime64[ns]")
    md_times = massdot.dt_utc.values.astype("datetime64[ns]")

    vz_lat = vz_attempt.lat.values
    vz_lon = vz_attempt.lon.values
    md_lat = massdot.lat.values
    md_lon = massdot.lon.values

    candidates = []  # (dist_m, vz_idx, md_idx)
    for i in range(len(vz_attempt)):
        time_diff_hours = np.abs((md_times - vz_times[i]) / np.timedelta64(1, "h"))
        time_ok = time_diff_hours <= MATCH_HOURS
        if not time_ok.any():
            continue
        dists = haversine_m(vz_lat[i], vz_lon[i], md_lat[time_ok], md_lon[time_ok])
        md_idxs = np.where(time_ok)[0]
        for md_idx, dist in zip(md_idxs, dists):
            if dist < MATCH_METERS:
                candidates.append((dist, i, md_idx))

    candidates.sort(key=lambda x: x[0])

    vz_matched = {}  # vz_idx -> (md_idx, dist)
    md_used = set()
    for dist, vz_idx, md_idx in candidates:
        if vz_idx in vz_matched or md_idx in md_used:
            continue
        vz_matched[vz_idx] = (md_idx, dist)
        md_used.add(md_idx)

    print(f"Matched pairs: {len(vz_matched)}")

    # build output features
    out_features = []

    # pre_massdot features
    for _, row in vz_pre.iterrows():
        props = dict(row.props)
        props["provenance"] = "pre_massdot"
        props["match_distance_m"] = None
        props["severity"] = None
        out_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row.lon, row.lat]},
                "properties": props,
            }
        )

    # attempted VZ features (both / vz_only)
    for i, row in vz_attempt.iterrows():
        props = dict(row.props)
        if i in vz_matched:
            md_idx, dist = vz_matched[i]
            props["provenance"] = "both"
            props["match_distance_m"] = round(float(dist), 2)
            props["severity"] = massdot.iloc[md_idx]["CRASH_SEVERITY_DESCR"]
        else:
            props["provenance"] = "vz_only"
            props["match_distance_m"] = None
            props["severity"] = None
        out_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row.lon, row.lat]},
                "properties": props,
            }
        )

    # massdot_only features
    massdot_only_count = 0
    for md_idx, md_row in massdot.iterrows():
        if md_idx in md_used:
            continue
        massdot_only_count += 1
        dt_utc = md_row["dt_utc"]
        street = md_row.get("RDWY")
        street = None if pd.isna(street) else str(street).strip()
        out_features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [md_row["lon"], md_row["lat"]]},
                "properties": {
                    "street": street,
                    "location_type": None,
                    "dispatch_ts": dt_utc.isoformat(),
                    "timestamp_ms": int(dt_utc.timestamp() * 1000),
                    "provenance": "massdot_only",
                    "match_distance_m": None,
                    "severity": md_row["CRASH_SEVERITY_DESCR"],
                },
            }
        )

    out_gj = {"type": "FeatureCollection", "features": out_features}
    OUTPUT.write_text(json.dumps(out_gj))
    print(f"\nWrote {OUTPUT} with {len(out_features)} features.")

    # ---- verification ----
    print("\n=== Per-year table (2021-2025) ===")
    print(f"{'Year':<6}{'VZ':>6}{'MassDOT':>9}{'matched':>9}{'vz_only':>9}{'md_only':>9}")
    for year in [2021, 2022, 2023, 2024, 2025]:
        vz_year_mask = vz_attempt.dt_utc.dt.year == year
        vz_year_idxs = vz_attempt.index[vz_year_mask]
        vz_count = vz_year_mask.sum()
        md_count = (massdot.dt_utc.dt.year == year).sum()
        matched = sum(1 for idx in vz_year_idxs if idx in vz_matched)
        vzonly = vz_count - matched
        # massdot_only for this year: massdot rows this year not in md_used
        md_year_idxs = massdot.index[massdot.dt_utc.dt.year == year]
        mdonly = sum(1 for idx in md_year_idxs if idx not in md_used)
        print(f"{year:<6}{vz_count:>6}{md_count:>9}{matched:>9}{vzonly:>9}{mdonly:>9}")

    print("\n=== 2023 check against hand-verified numbers ===")
    dists_2023 = [
        dist
        for idx, (md_idx, dist) in vz_matched.items()
        if vz_attempt.iloc[idx].dt_utc.year == 2023
    ]
    if dists_2023:
        print(f"2023 matched count: {len(dists_2023)} (expected ~45)")
        print(f"2023 median match distance: {np.median(dists_2023):.2f} m (expected ~8m)")
    else:
        print("2023: NO MATCHES FOUND - investigate before trusting other years")

    print("\n=== Total feature count & provenance breakdown ===")
    print(f"Total features: {len(out_features)}")
    prov_counts = {}
    for feat in out_features:
        p = feat["properties"]["provenance"]
        prov_counts[p] = prov_counts.get(p, 0) + 1
    for k in ["both", "vz_only", "massdot_only", "pre_massdot"]:
        print(f"  {k}: {prov_counts.get(k, 0)}")


if __name__ == "__main__":
    main()
