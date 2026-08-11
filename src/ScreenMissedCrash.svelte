<script>
  import { onMount } from 'svelte';

  // Selected + independently re-verified against the pipeline's own logic
  // on 2026-08-10 (see scripts/match_crashes.py for the matching method
  // this re-check replicates, and data/massdot_boston_bike_crashes.csv for
  // the source it was checked against). Selection method: filtered
  // public/data/boston_bike_crashes_enriched.geojson to
  // provenance === 'vz_only' && location_type === 'Intersection', then
  // matched by exact dispatch_ts + lat/long against a raw Vision Zero CKAN
  // pull to recover xstreet1/xstreet2/mode_type — scripts/fetch_crash_data.py
  // never carries those three columns into the committed GeoJSON (only
  // street/location_type/dispatch_ts/timestamp_ms survive), so they can't
  // be fetched client-side and are pinned here instead. Re-verified zero
  // MassDOT rows fall within +/-2 hours of this dispatch_ts at all (so the
  // 100m radius check is moot) using the exact haversine +
  // America/New_York-localization logic in scripts/match_crashes.py.
  // If the pipeline is ever re-run and this record's provenance changes
  // from vz_only, this selection must be redone by hand — there is no
  // client-side way to regenerate it, since the raw xstreet1/xstreet2
  // source isn't part of the deployed data.
  const RECORD = {
    dispatchTimestampMs: 1675169131000, // 2023-01-31T12:45:31+00:00
    locationType: 'Intersection',
    crossStreetA: 'Marlborough St',
    crossStreetB: 'Massachusetts Ave',
    lat: 42.35006295890982,
    lon: -71.0890957622328,
    mode: 'Bicycle',
  };
  const MATCH_WINDOW_MS = 2 * 60 * 60 * 1000; // matches MATCH_HOURS in scripts/match_crashes.py
  const DATE_TIME_FMT = { month: 'long', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' };
  const DATE_FMT = { month: 'long', day: 'numeric', year: 'numeric' };

  const dispatchDate = new Date(RECORD.dispatchTimestampMs);
  const windowStart = new Date(RECORD.dispatchTimestampMs - MATCH_WINDOW_MS);
  const windowEnd = new Date(RECORD.dispatchTimestampMs + MATCH_WINDOW_MS);
  const dispatchLabel = dispatchDate.toLocaleString('en-US', DATE_TIME_FMT);
  const dispatchDateOnly = dispatchDate.toLocaleDateString('en-US', DATE_FMT);
  const windowLabel = `${windowStart.toLocaleString('en-US', DATE_TIME_FMT)} – ${windowEnd.toLocaleString('en-US', DATE_TIME_FMT)}`;

  // Live count, not hardcoded — same source and provenance filter the
  // heatmap/explorer screens already use for their 74% / vz_only figures.
  const CRASH_DATA_URL = `${import.meta.env.BASE_URL}data/boston_bike_crashes_enriched.geojson`;
  let liveVzOnlyCount = null;
  let loadError = null;

  onMount(async () => {
    try {
      const res = await fetch(CRASH_DATA_URL);
      if (!res.ok) throw new Error(`fetch failed: ${res.status}`);
      const geojson = await res.json();
      liveVzOnlyCount = geojson.features.filter((f) => f.properties.provenance === 'vz_only').length;
    } catch (e) {
      loadError = e.message;
      console.warn('Could not load live vz_only count:', e.message);
    }
  });
</script>

<section class="missed-crash-screen">
  <div class="content">
    <h2 class="headline">Here's what a <span class="accent">missed</span> crash actually looks like.</h2>
    <p class="subhead">
      Left: a real 911 dispatch record. Right: the real result of searching MassDOT's crash database for that same
      time and place.
    </p>

    <div class="record-panels">
      <div class="record-panel panel-dispatch">
        <div class="panel-label"><span class="panel-dot panel-dot-blue"></span>Boston 911 Dispatch</div>
        <div class="field">
          <div class="field-label">Dispatch time</div>
          <div class="field-value">{dispatchLabel}</div>
        </div>
        <div class="field">
          <div class="field-label">Location type</div>
          <div class="field-value">{RECORD.locationType}</div>
        </div>
        <div class="field">
          <div class="field-label">Cross streets</div>
          <div class="field-value">{RECORD.crossStreetA} &amp; {RECORD.crossStreetB}</div>
        </div>
        <div class="field">
          <div class="field-label">Coordinates</div>
          <div class="field-value">{RECORD.lat.toFixed(5)}, {RECORD.lon.toFixed(5)}</div>
        </div>
        <div class="field">
          <div class="field-label">Mode</div>
          <div class="field-value">{RECORD.mode}</div>
        </div>
      </div>

      <div class="record-panel panel-massdot">
        <div class="panel-label">
          <span class="panel-dot panel-dot-grey"></span>MassDOT <span class="panel-label-sub">(police crash database)</span>
        </div>
        <div class="field">
          <div class="field-label">Time window (&plusmn;2h)</div>
          <div class="field-value">{windowLabel}</div>
        </div>
        <div class="field">
          <div class="field-label">Radius</div>
          <div class="field-value">100 meters</div>
        </div>
        <div class="field">
          <div class="field-label">Center</div>
          <div class="field-value">{RECORD.lat.toFixed(5)}, {RECORD.lon.toFixed(5)}</div>
        </div>
        <div class="field">
          <div class="field-label">Mode</div>
          <div class="field-value">{RECORD.mode}</div>
        </div>
        <div class="empty-result">No matching entry found.</div>
      </div>
    </div>

    <p class="pivot-caption">
      The dispatch record: {RECORD.crossStreetA} and {RECORD.crossStreetB}, {dispatchDateOnly} has no matching
      entry in MassDOT's database.
    </p>
    <p class="pivot-followup">
      {#if loadError}
        Live count unavailable ({loadError}).
      {:else if liveVzOnlyCount !== null}
        There are <span class="count-pink">{liveVzOnlyCount.toLocaleString()}</span> more like it
      {:else}
        Loading the citywide count…
      {/if}
    </p>
  </div>
</section>

<style>
  .missed-crash-screen {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: #000;
    padding: 2.5rem 3rem 5.5rem;
    box-sizing: border-box;
  }
  .content {
    max-width: 54rem;
    width: 100%;
  }
  .headline {
    margin: 0 0 0.6rem;
    font-size: clamp(1.5rem, 3.4vw, 2.3rem);
    font-weight: 600;
    line-height: 1.35;
    color: #fff;
  }
  .accent {
    color: #ff4fa2;
  }
  .subhead {
    margin: 0 0 1.75rem;
    color: #fff;
    font-size: 0.85rem;
    line-height: 1.5;
  }
  .record-panels {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
  /* Simple bordered boxes (2026-08-11), not elevated cards — no
     box-shadow, no rounded corners, no distinct panel-fill background
     lifting them off the page. Border color alone carries the meaning:
     blue (same source color as THE GAP's "911 dispatch only" swatch) for
     the dispatch box, plain gray (reused from this file's own prior
     border-top treatment) for the MassDOT box. */
  .record-panel {
    border: 1px solid #444;
    padding: 1.1rem 1.25rem;
    background: transparent;
  }
  .panel-dispatch {
    border-color: #7fb2e5;
  }
  .panel-massdot {
    border-color: #444;
  }
  .panel-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.95rem;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #ccc;
  }
  .panel-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    flex: none;
  }
  .panel-dot-blue {
    background: #7fb2e5;
  }
  .panel-dot-grey {
    background: #555;
  }
  .panel-label-sub {
    text-transform: none;
    font-weight: 400;
    letter-spacing: normal;
    font-size: 0.62rem;
    color: #888;
  }
  .field {
    margin-bottom: 0.65rem;
  }
  .field:last-child {
    margin-bottom: 0;
  }
  .field-label {
    font-size: 0.62rem;
    color: #777;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.15rem;
  }
  .field-value {
    font-size: 0.82rem;
    color: #f2f2f2;
    line-height: 1.35;
  }
  /* The punchline: a solid white box (not an outline) with black text, so
     the absence of a match reads as the loudest thing in the MassDOT
     panel rather than a muted placeholder. */
  .empty-result {
    margin-top: 0.9rem;
    padding: 0.75rem;
    background: #fff;
    text-align: center;
    color: #000;
    font-size: 0.78rem;
    font-style: italic;
  }
  .pivot-caption {
    margin: 1.75rem 0 0;
    color: #fff;
    font-size: 1.2rem;
    line-height: 1.5;
    font-weight: 500;
  }
  .pivot-followup {
    margin: 0.5rem 0 0;
    color: #fff;
    font-size: 1.2rem;
    line-height: 1.5;
    font-weight: 500;
  }
  .count-pink {
    color: #ff4fa2;
    font-weight: 700;
  }
  @media (max-width: 700px) {
    .record-panels {
      grid-template-columns: 1fr;
    }
  }
</style>
