<script>
  import { onMount } from 'svelte';

  export let selectedRange = null; // { start: Date, end: Date } | null = full range
  export let activeProvenance = null; // Set of provenance keys shown; null/undefined = show all

  const CRASH_DATA_URL = `${import.meta.env.BASE_URL}data/boston_bike_crashes_enriched.geojson`;
  const ALL_PROVENANCE = ['both', 'vz_only', 'massdot_only'];

  let features = [];
  let loadError = null;

  onMount(async () => {
    try {
      const res = await fetch(CRASH_DATA_URL);
      if (!res.ok) throw new Error(`fetch failed: ${res.status}`);
      const geojson = await res.json();
      // Same scope as the map on this screen: pre_massdot excluded.
      features = geojson.features.filter((f) => f.properties.provenance !== 'pre_massdot');
    } catch (e) {
      loadError = e.message;
      console.warn('Could not load crash data for stat counter:', e.message);
    }
  });

  // Mirrors CrashMap.svelte's own filter exactly (date range + provenance
  // toggle) so this number always matches what's actually drawn on the
  // map, not just the date-filtered subset.
  $: activeList = activeProvenance ? [...activeProvenance] : ALL_PROVENANCE;
  $: visible = features.filter((f) => {
    if (!activeList.includes(f.properties.provenance)) return false;
    if (!selectedRange) return true;
    const ts = f.properties.timestamp_ms;
    return ts >= selectedRange.start.getTime() && ts <= selectedRange.end.getTime();
  });

  $: counts = {
    both: visible.filter((f) => f.properties.provenance === 'both').length,
    vz_only: visible.filter((f) => f.properties.provenance === 'vz_only').length,
    massdot_only: visible.filter((f) => f.properties.provenance === 'massdot_only').length,
  };
</script>

{#if !loadError}
  <p class="record-count">Count of records: {visible.length.toLocaleString()} reported bike crashes shown on the map</p>
  <div class="stat-counter">
    <div class="stat">
      <div class="n" style="color: #e28aab">{counts.both.toLocaleString()}</div>
      <div class="label">both sources</div>
    </div>
    <div class="stat">
      <div class="n" style="color: #7fb2e5">{counts.vz_only.toLocaleString()}</div>
      <div class="label">911 dispatch only</div>
    </div>
    <div class="stat">
      <div class="n" style="color: #f2d06b">{counts.massdot_only.toLocaleString()}</div>
      <div class="label">police report only</div>
    </div>
  </div>
{/if}

<style>
  .record-count {
    margin: 0.5rem 0 0.4rem;
    color: #fff;
    font-size: 0.8rem;
    font-variant-numeric: tabular-nums;
  }
  .stat-counter {
    display: flex;
    gap: 1.5rem;
    margin: 0.75rem 0 1rem;
    padding: 0.6rem 0.75rem;
    border: 1px solid #333;
    border-radius: 6px;
    background: #0d0d0d;
  }
  .stat {
    flex: 1;
    text-align: center;
  }
  .n {
    font-size: 1.3rem;
    font-weight: 700;
    line-height: 1;
    font-variant-numeric: tabular-nums;
  }
  .label {
    margin-top: 0.25rem;
    color: #fff;
    font-size: 0.68rem;
    line-height: 1.3;
  }
</style>
