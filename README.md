# Boston Bike Crash Explorer

A single-page interactive explorable of reported bicycle crashes in Boston.
Full context, scope, guardrails, and working style: see `CLAUDE.md`
(Claude Code reads this automatically).

## Setup

```bash
npm install
npm run dev
```

## Data pipeline

```bash
pip install pandas requests --break-system-packages
python scripts/fetch_crash_data.py
mkdir -p public/data
cp data/boston_bike_crashes.geojson public/data/
```

## Structure

```
src/
  App.svelte       — layout, wires TimeChart's brushed range to CrashMap's filter
  TimeChart.svelte — D3 chart with brush-to-select (the core interaction mechanic)
  CrashMap.svelte  — MapLibre map, crash points filtered by the brushed range
scripts/
  fetch_crash_data.py — pulls real data from the Vision Zero CKAN API
```

## Status
Scaffolded with placeholder chart data and no map data loaded yet — the
brush→filter wiring works end-to-end, but needs real data from
`scripts/fetch_crash_data.py` before it means anything. See CLAUDE.md
"Open questions" and "Weekend build order."
