# Boston Bike Crash Explorer — Project Context

## What this is
A single-page interactive explorable of reported bicycle crashes in Boston.
Portfolio piece for a Data Visualization Engineer application at Planet
(satellite imagery / Earth observation company) — but this piece is
deliberately NOT framed around Planet. It's a genuine, personally-motivated
project about a real local issue (Boston cycling safety), built to be an
impressive, highly interactive, non-generic geospatial visualization.

## Reference / quality bar
Modeled on jbvordick.github.io/airQualityInteractive (Jillian Vordick,
"Pittsburgh Air Quality"). Confirmed structure from a screenshot of the live
site:
- A time-series chart (AQI over time, category-band background shading,
  average line + percentile band, "Count of records: N" annotation, a
  "Show Points" toggle) sits next to a real labeled map (street names,
  landmarks visible — an actual basemap, not an abstract shape).
- **The core mechanic: drag-to-brush a date range on the time chart, and the
  map instantly filters to just that range.** "Selected dates: X to Y" is
  displayed live. This brush-linked-views pattern is the single most
  important thing to replicate well.
- A few curated, clickable callout boxes on the map jump to specific
  interesting date windows (e.g. "click to see reports during the Covid
  shutdown, 03/01/2020–06/01/2020"). This is a light narrative layer
  layered into free exploration — NOT full scrollytelling.
- A search box to filter records by text/location.
- Their dataset is huge (110,690 smell reports) requiring performance
  engineering. **Ours is much smaller (~3,500–4,500 Boston bike crashes
  total) — plain SVG/D3 circles will perform fine. Do not over-engineer
  rendering.**

## What we're trying to show (drives every design decision)
Where and when do reported bike crashes happen in Boston, and does that
pattern shift around known policy/infrastructure changes? We are NOT
claiming which streets are "most dangerous" (no ridership/exposure data
to normalize against) — only showing reported-crash patterns, honestly
framed.

## Scope

### Phase 1 (this build)
- Brush-linked time chart ↔ map, filtering live (the core mechanic —
  build and polish this first, before anything else)
- Real labeled MapLibre basemap (open style, e.g. OpenFreeMap/Protomaps —
  NOT a blank/abstract background; street names matter to this story)
- Curated callouts, POLICY/INFRASTRUCTURE ONLY for this phase:
  - 2017-01-09: Boston's default speed limit dropped 30→25mph
  - Mass Ave protected bike lane installation (confirm exact date during
    build from Boston bike-network vintage data)
  - Comm Ave protected bike lane installation (confirm exact date)
  - 2020 COVID ridership dip (roughly March–June 2020)
- Street name search/filter (Vision Zero data has a `street` field)
- Visible methodology note: denominator/exposure caveat (raw crash counts
  ≠ risk without ridership data) and reporting-bias caveat (only
  police/EMS-reported crashes are captured)
- "Count of records: N" style annotations on the chart, matching the
  reference's credibility touches

### Phase 2 (explicitly NOT this build — do not add without being asked)
- Specific notable individual crashes/fatalities as callouts. This needs
  careful, deliberate handling (real people, real tragedies) and should
  not be rushed into a weekend sprint. Wait for explicit go-ahead.

### Explicitly out of scope, don't add
- No routing tool ("build a safer route")
- No severity color-styling unless a MassDOT join is clean and fast —
  default to unstyled points; treat severity styling as a stretch goal
- No multi-corridor before/after case-study mode — that's a different,
  bigger project
- No vector-tile pipeline (PMTiles/tippecanoe) — data volume is small
  enough that plain GeoJSON is the right choice; don't add tiling
  infrastructure that isn't needed

## Structure (updated 2026-07-26 — supersedes the single-screen decision above)
As of 2026-07-26 the app is a 5-screen vertical scroll sequence (hook →
full-map stat card → "The Gap" explorer → "What People Are Afraid Of" →
closing text), explicitly overriding the earlier "single explorable
screen, no scrollytelling" decision. Each screen is `min-height: 100vh`.
Screens 3 and 4 keep the brush/chart/map interactivity built in Phase 1;
screen 3 additionally has suggestion chips, a live provenance stat
counter, pulsing crash dots, and a click-to-inspect detail card.

## Data sources (verified — use these exact endpoints)

**Primary: Vision Zero Crash Records (Analyze Boston)**
- Landing page: https://data.boston.gov/dataset/vision-zero-crash-records
- Resource id: `e4bfe397-6bfc-49c5-9367-c879fac7401d`
- CSV dump: `https://data.boston.gov/datastore/dump/e4bfe397-6bfc-49c5-9367-c879fac7401d?bom=True`
- CKAN search API: `https://data.boston.gov/api/3/action/datastore_search?resource_id=e4bfe397-6bfc-49c5-9367-c879fac7401d`
- Schema (10 columns, confirmed from live CSV):
  `dispatch_ts, mode_type, location_type, street, xstreet1, xstreet2, x_cord, y_cord, lat, long`
  - Filter `mode_type == 'bike'`
  - `dispatch_ts` format: `YYYY-MM-DD HH:MM:SS+00` (UTC, single combined field)
  - `lat`/`long` are decimal degrees (note: column is literally named `long`)
  - `x_cord`/`y_cord` are MA State Plane feet — ignore these, use lat/long
- Coverage: 2015-01-01 → present, monthly updates
- KNOWN LIMITATION: no severity/injury field in this file — do not imply
  severity from this dataset alone
- Companion: Vision Zero Fatality Records —
  https://data.boston.gov/dataset/vision-zero-fatality-records
  (BPD-verified fatalities; separate file, has crash type). Relevant for
  Phase 2 only — do not merge into Phase 1 map styling.

**Secondary/enrichment (optional, Phase 1 stretch): MassDOT IMPACT crashes**
- Portal: https://massdot-impact-crashes-vhb.opendata.arcgis.com/
- ArcGIS REST example: `https://gis.crashdata.dot.mass.gov/arcgis/rest/services/MassDOT/MASSDOT_ODP_OPEN_2025/FeatureServer/0`
- Has `CRASH_SEVERITY_DESCR`, `NUMB_FATAL_INJR`, `NUMB_NONFATAL_INJR`, weather,
  contributing-factor fields — richer than Vision Zero but no shared crash ID,
  so any join is best-effort. Only pursue if Phase 1 core mechanic is done
  and there's time left.

**Infrastructure: Boston bike network**
- Existing Bike Network 2024 (Analyze Boston / BostonMaps ArcGIS Hub),
  e.g. https://data.boston.gov/dataset/existing-bike-network-2024
- Use this to confirm exact protected-lane installation dates for the
  Mass Ave / Comm Ave callouts, and optionally as a toggle-able layer.

## Guardrails (do not violate when writing copy/captions)
- Never claim a street/intersection is "most dangerous" from raw crash
  counts alone — no ridership/exposure data means no risk ranking, only
  reported-incident density. Say "reported crashes," not "danger" or "risk."
- Never imply causation between a policy/infrastructure change and a
  crash-count change shown in the same view — correlation only, and note
  plausible confounders (COVID ridership swings, other concurrent changes).
- Never fabricate or estimate a data point. If a number isn't in the
  actual downloaded file, don't state it — verify by querying the local
  data file directly, every time, before it appears in the UI copy.
- Any specific number, date, or fact used in a callout must be checked
  against the actual downloaded data file, not asserted from memory or
  general web knowledge.
- Phase 2 (individual crash/fatality callouts) is explicitly out of scope
  until the project owner asks for it directly — do not add "just in case."

## Working style (how we work together — read this every session)
1. Work in small, named steps, not one big pass. After each step, STOP
   and report in plain language what you did, why, and what changed.
   Don't move to the next step until the owner responds.
2. Commit after each completed step with a clear commit message.
3. If about to deviate from anything in this file (data source, scope,
   stack choice), STOP and ask first.
4. If a command fails, hangs, or takes longer than ~30 seconds with no
   output, STOP immediately and show the exact error. Do not silently
   retry the same approach multiple times — this has caused a stuck loop
   before (a `pip install geopandas` dependency issue). If a Python
   geospatial package is missing, prefer `brew install <pkg>` over `pip`
   for anything GDAL-backed.
5. Don't chain multiple risky/long-running commands in one go — download,
   then stop and confirm before processing; process, then stop and confirm
   before rendering.

## Stack
- Svelte + Vite (app shell)
- D3.js (time chart with brush, category-band shading)
- MapLibre GL JS (real labeled basemap + crash points as a GeoJSON source)
- Python + pandas/geopandas (data pull/clean from Vision Zero CKAN API)
- No PMTiles/tippecanoe needed at this data volume — plain GeoJSON

## Weekend build order
1. Data: pull Vision Zero bike-crash rows via CKAN API, confirm real
   count and date range from the actual file (see scripts/fetch_crash_data.py)
2. Static map: render crash points on a real labeled MapLibre basemap,
   no filtering yet — get the visual right first
3. Time chart: D3 area/line chart of crash counts over time, styled with
   background bands if a natural category exists (else keep it simple)
4. Wire the brush: dragging a selection on the chart filters the map's
   visible points live — this is the core mechanic, get it right
5. Callouts: add the 3-4 Phase 1 policy/infrastructure callouts as
   clickable buttons/markers that set the brush to a specific date range
6. Search: street-name filter box
7. Methodology note + polish + deploy

## Open questions
- [x] Exact Mass Ave protected-lane installation date — resolved
      2026-07-26 from Boston's Existing Bike Network 2024 ArcGIS
      FeatureServer (`Boston_Bicycle_Network_2024`, field `InstallDat`/
      `ExisFacil`). There is no single install date — Mass Ave's
      separated bike lane (`SBL`/`SBLBL`) was built in phases: 14
      segments in 2016, 4 in 2020, 5 in 2022, 19 in 2023, 1 in 2024. 2016
      is the first major phase (used for the Screen 3 "Mass Ave corridor"
      suggestion chip, since 2020/2023 are already covered by the other
      chips). Comm Ave was not looked up — still open if needed later.
- [ ] Whether MassDOT severity enrichment is worth pursuing this weekend
      or left for later
