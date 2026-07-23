<script>
  import TimeChart from './TimeChart.svelte';
  import CrashMap from './CrashMap.svelte';
  import ConcernBarChart from './ConcernBarChart.svelte';

  // The core linked-views mechanic: TimeChart dispatches a brushed date
  // range, CrashMap filters its points to match. Both start showing the
  // full data range until real data + brush are wired in.
  let selectedRange = null; // { start: Date, end: Date } | null = full range

  // Provenance legend doubles as a map filter: each entry toggles whether
  // that crash-match category is shown. Swatch styles here must stay in
  // sync with the circle paint spec in CrashMap.svelte.
  const provenanceLegend = [
    { key: 'both', label: 'Confirmed by both sources', swatch: 'solid' },
    { key: 'vz_only', label: '911 dispatch only \u2014 no police report', swatch: 'hollow' },
    { key: 'massdot_only', label: 'Police report only \u2014 no dispatch match', swatch: 'white' },
    { key: 'pre_massdot', label: 'No MassDOT data available (2015\u20132020, 2026)', swatch: 'faint' },
  ];

  let activeProvenance = new Set(provenanceLegend.map((p) => p.key));

  // Layer 2 ("Fear Layer") — citizen-submitted safety concerns, off by
  // default until the full tab experience is designed around it.
  let showConcerns = false;

  function toggleProvenance(key) {
    const next = new Set(activeProvenance);
    if (next.has(key)) {
      next.delete(key);
    } else {
      next.add(key);
    }
    activeProvenance = next;
  }

  function resetRange() {
    selectedRange = null;
  }
</script>

<main>
  <header>
    <h1>What Boston Doesn't Know About Bike Crashes</h1>
    <p class="selected-dates">
      {#if selectedRange}
        Selected dates: {selectedRange.start.toLocaleDateString()} to {selectedRange.end.toLocaleDateString()}
        <button on:click={resetRange}>Reset</button>
      {:else}
        Selected dates: full range
      {/if}
    </p>
  </header>

  <div class="panels">
    <section class="chart-panel">
      <TimeChart bind:selectedRange />

      <div class="legend">
        <h4>Crash-match provenance <span class="legend-hint">(click to filter)</span></h4>
        {#each provenanceLegend as p}
          <button
            class="legend-item"
            class:inactive={!activeProvenance.has(p.key)}
            on:click={() => toggleProvenance(p.key)}
          >
            <span class="swatch swatch-{p.swatch}"></span>
            {p.label}
          </button>
        {/each}
      </div>

      <label class="concerns-toggle">
        <input type="checkbox" bind:checked={showConcerns} />
        Show safety concerns (176 bike-related reports)
      </label>

      {#if showConcerns}
        <ConcernBarChart />
      {/if}
    </section>

    <section class="map-panel">
      <CrashMap {selectedRange} {activeProvenance} {showConcerns} />
    </section>
  </div>

  <footer>
    <p>
      <strong>What this shows:</strong> reported bicycle crash locations and timing.
      <strong>What this doesn't show:</strong> risk or danger — comparing raw crash
      counts between locations requires ridership data we don't have, so no
      street is labeled "most dangerous" here. Only police/EMS-reported
      crashes are captured; near-misses and unreported incidents aren't
      included. Source:
      <a href="https://data.boston.gov/dataset/vision-zero-crash-records" target="_blank" rel="noopener">
        Boston Vision Zero Crash Records
      </a>.
    </p>
  </footer>
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #000;
    color: #fff;
    font-family: ui-monospace, 'SFMono-Regular', 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
  }
  header {
    padding: 1rem 1.5rem 0.5rem;
  }
  h1 {
    margin: 0;
    font-size: 1.4rem;
  }
  .selected-dates {
    font-weight: 600;
    margin: 0.5rem 0 0;
  }
  .selected-dates button {
    font-family: inherit;
    background: none;
    border: 1px solid #555;
    color: #fff;
    border-radius: 4px;
    padding: 0.15rem 0.5rem;
    margin-left: 0.5rem;
    cursor: pointer;
  }
  .selected-dates button:hover {
    border-color: #ff4fa2;
    color: #ff4fa2;
  }
  .panels {
    flex: 1;
    display: flex;
    min-height: 0;
  }
  .chart-panel {
    width: 40%;
    padding: 1rem 1.5rem;
    overflow-y: auto;
  }
  .map-panel {
    flex: 1;
  }
  .legend {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-top: 1rem;
  }
  .legend h4 {
    margin: 0 0 0.25rem;
    font-size: 0.85rem;
    color: #ccc;
    font-weight: 600;
  }
  .legend-hint {
    color: #777;
    font-weight: 400;
  }
  .legend-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    text-align: left;
    padding: 0.4rem 0.6rem;
    border: 1px solid #444;
    border-radius: 6px;
    background: #111;
    color: #fff;
    cursor: pointer;
    font-size: 0.82rem;
    font-family: inherit;
    opacity: 1;
    transition: opacity 0.15s, border-color 0.15s;
  }
  .legend-item:hover {
    border-color: #ff4fa2;
  }
  .legend-item.inactive {
    opacity: 0.4;
  }
  .swatch {
    flex: none;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    box-sizing: border-box;
  }
  .swatch-solid {
    background: #ff4fa2;
  }
  .swatch-hollow {
    background: transparent;
    border: 1.5px solid #ff4fa2;
  }
  .swatch-white {
    background: #ffffff;
  }
  .swatch-faint {
    background: transparent;
    border: 1px solid rgba(255, 79, 162, 0.35);
  }
  .concerns-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1rem;
    padding: 0.4rem 0.6rem;
    border: 1px solid #444;
    border-radius: 6px;
    color: #ffb444;
    font-size: 0.82rem;
    cursor: pointer;
  }
  footer {
    padding: 0.75rem 1.5rem;
    font-size: 0.8rem;
    color: #aaa;
    border-top: 1px solid #222;
  }
  footer a {
    color: #ff4fa2;
  }
</style>
