<script>
  import TimeChart from './TimeChart.svelte';
  import CrashMap from './CrashMap.svelte';

  // The core linked-views mechanic: TimeChart dispatches a brushed date
  // range, CrashMap filters its points to match. Both start showing the
  // full data range until real data + brush are wired in.
  let selectedRange = null; // { start: Date, end: Date } | null = full range

  // TODO (Phase 1, step 5): populate with real dates confirmed from the
  // bike network vintage data + Vision Zero speed-limit change date.
  const callouts = [
    {
      label: 'Speed limit dropped 30\u219225mph (Jan 2017)',
      start: '2017-01-01',
      end: '2017-04-01',
    },
    // { label: 'Mass Ave protected lane installed', start: '____', end: '____' },
    // { label: 'Comm Ave protected lane installed', start: '____', end: '____' },
    {
      label: 'COVID ridership dip',
      start: '2020-03-01',
      end: '2020-06-01',
    },
  ];

  function jumpTo(range) {
    selectedRange = { start: new Date(range.start), end: new Date(range.end) };
  }

  function resetRange() {
    selectedRange = null;
  }
</script>

<main>
  <header>
    <h1>Boston Bike Crash Explorer</h1>
    <p class="subtitle">Reported bicycle crashes, City of Boston Vision Zero data</p>
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

      <div class="callouts">
        {#each callouts as c}
          <button class="callout" on:click={() => jumpTo(c)}>{c.label}</button>
        {/each}
      </div>
    </section>

    <section class="map-panel">
      <CrashMap {selectedRange} />
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
  .subtitle {
    margin: 0.2rem 0 0;
    color: #aaa;
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
  .callouts {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 1rem;
  }
  .callout {
    text-align: left;
    padding: 0.5rem 0.75rem;
    border: 1px solid #444;
    border-radius: 6px;
    background: #111;
    color: #fff;
    cursor: pointer;
    font-size: 0.9rem;
    font-family: inherit;
  }
  .callout:hover {
    background: #1a1a1a;
    border-color: #ff4fa2;
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
