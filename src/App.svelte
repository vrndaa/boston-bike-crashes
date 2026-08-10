<script>
  import TimeChart from './TimeChart.svelte';
  import CrashMap from './CrashMap.svelte';
  import ConcernBarChart from './ConcernBarChart.svelte';
  import LiveStatCounter from './LiveStatCounter.svelte';
  import Screen1Hook from './Screen1Hook.svelte';
  import ScreenChapterDivider from './ScreenChapterDivider.svelte';
  import ScreenMissedCrash from './ScreenMissedCrash.svelte';
  import Screen2Hero from './Screen2Hero.svelte';
  import ScreenQuotes from './ScreenQuotes.svelte';
  import Screen5Closing from './Screen5Closing.svelte';

  // Button/breadcrumb navigation (2026-07-26), replacing scroll. Every
  // screen stays mounted the whole time — only CSS display toggles which
  // one shows — so the brush selection, map pan/zoom, and stat-card
  // dismissal all survive navigating away and back. The tradeoff is that
  // the map/chart components need to know when they've become visible
  // again, since a MapLibre canvas or an SVG chart built while its
  // container is display:none measures 0 width and never fixes itself
  // without being told to — see the `visible` prop on CrashMap, HeroMap,
  // and TimeChart.
  // 0=hook, 1=chapter1, 2=missed-crash, 3=hero, 4=explorer, 5=chapter2,
  // 6=quotes, 7=fear, 8=closing
  const LAST_SCREEN = 8;
  let currentScreen = 0;
  let furthestReached = 0; // drives how much of the breadcrumb is filled

  function goTo(i) {
    currentScreen = i;
    furthestReached = Math.max(furthestReached, i);
  }
  function next() {
    if (currentScreen < LAST_SCREEN) goTo(currentScreen + 1);
  }
  function back() {
    if (currentScreen > 0) goTo(currentScreen - 1);
  }

  // The core linked-views mechanic: TimeChart dispatches a brushed date
  // range, CrashMap filters its points to match. Used on the explorer
  // screen (now Screen 5).
  let selectedRange = null; // { start: Date, end: Date } | null = full range

  // Provenance legend doubles as a map filter: each entry toggles whether
  // that crash-match category is shown. Swatch styles here must stay in
  // sync with the circle paint spec in CrashMap.svelte. pre_massdot is
  // excluded from this view entirely — no legend entry, no dim/muted dot,
  // no footnote.
  // Recolored 2026-07-28 to match Screen 2's stat-number palette exactly
  // (#e28aab / #7fb2e5 / #f2d06b) for consistency across the piece —
  // this replaces the brighter #ff4fa2/#4fc3f7/white Screen 3 used before.
  const provenanceLegend = [
    { key: 'both', label: 'Confirmed by both sources', swatch: 'pink' },
    { key: 'vz_only', label: '911 dispatch only — no police report', swatch: 'blue' },
    { key: 'massdot_only', label: 'Police report only — no dispatch match', swatch: 'yellow' },
  ];

  // Static orientation label for the fear screen — verified against
  // public/data/safety_concerns.geojson (176 mode=='bike' rows) in this
  // session; not reactive to any filter.
  const CONCERN_COUNT = 176;

  let activeProvenance = new Set(provenanceLegend.map((p) => p.key));

  function toggleProvenance(key) {
    const next = new Set(activeProvenance);
    if (next.has(key)) {
      next.delete(key);
    } else {
      next.add(key);
    }
    activeProvenance = next;
  }

  // Fear-map corridor callouts (2026-07-27, repositioned 2026-07-28).
  // Verified by literal keyword search across all 176 bike-mode concern
  // comments — NOT the earlier 150m spatial-clustering pass, which came
  // back a near-tie (10 vs 10) between these same two corridors and
  // wasn't clean enough to declare a single "top cluster." Mention counts
  // and center coordinates are exact re-runs, not reused from the spatial
  // analysis:
  //   Longwood/Riverway/Ave Louis Pasteur: 9 of 176 (bikefacility 5, yieldturn 4)
  //   Mass Ave / Massachusetts Ave: 12 of 176 (bikefacility 6, other 2,
  //     walksignal 1, yieldturn 1, runlightssigns 1, roadwaymaint 1)
  // Copy intentionally does NOT claim "confirmed by two independent
  // methods" — flagged back to the project owner that this doesn't hold
  // up on rigorous re-check (grid rounding and keyword count both put
  // Mass Ave slightly ahead of Longwood; only a corridor-level merge of
  // two adjacent Longwood clusters gets it to 17). Sticking with the
  // verified mention counts instead of the stronger claim.
  const concernCallouts = [
    {
      lat: 42.33853,
      lon: -71.1064,
      title: 'Longwood Medical Area',
      count: 9,
      reason: 'Most-cited reasons: bike facilities missing/inadequate, drivers failing to yield on turns',
      corner: 'top-right',
    },
    {
      lat: 42.3403,
      lon: -71.07926,
      title: 'Mass Ave',
      count: 12,
      reason: 'Most-cited reason: bike facilities missing or inadequate',
      corner: 'top-left',
    },
  ];
</script>

<main>
  <div class="screen-slot" class:visible={currentScreen === 0}>
    <Screen1Hook />
  </div>

  <div class="screen-slot" class:visible={currentScreen === 1}>
    <ScreenChapterDivider text="What Gets Counted" chapterLabel="Chapter One" labelColor="#e28aab" />
  </div>

  <div class="screen-slot" class:visible={currentScreen === 2}>
    <ScreenMissedCrash />
  </div>

  <div class="screen-slot" class:visible={currentScreen === 3}>
    <Screen2Hero visible={currentScreen === 3} />
  </div>

  <div class="screen-slot" class:visible={currentScreen === 4}>
    <section class="screen explorer-screen">
      <div class="panels">
        <section class="chart-panel">
          <h2 class="screen-eyebrow">The Gap</h2>

          <p class="data-source-label">
            Reported bike crashes from Boston's Vision Zero 911 dispatch and MassDOT crash reports.
          </p>

          <TimeChart bind:selectedRange visible={currentScreen === 4} />

          <LiveStatCounter {selectedRange} {activeProvenance} />

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
        </section>

        <section class="map-panel">
          <CrashMap {selectedRange} {activeProvenance} showCrashes={true} showConcerns={false} visible={currentScreen === 4} />
        </section>
      </div>
    </section>
  </div>

  <div class="screen-slot" class:visible={currentScreen === 5}>
    <ScreenChapterDivider text="What It Cost in Human Terms" chapterLabel="Chapter Two" labelColor="var(--color-chapter2)" />
  </div>

  <div class="screen-slot" class:visible={currentScreen === 6}>
    <ScreenQuotes />
  </div>

  <div class="screen-slot" class:visible={currentScreen === 7}>
    <section class="screen fear-screen">
      <div class="panels">
        <section class="chart-panel">
          <h2 class="screen-eyebrow">What People Are Afraid Of</h2>

          <p class="data-source-label">
            What you're looking at: {CONCERN_COUNT.toLocaleString()} bike safety concerns submitted by Boston
            residents (2022–2026), from the city's Vision Zero reporting tool.
          </p>

          <ConcernBarChart />

          <p class="null-model-note">
            <strong>A note on what we didn't find.</strong> We checked whether safety concerns cluster where
            crashes actually happen — testing if fear predicts danger. At first it looked striking: 95.5% of
            concerns had a crash within 150 meters. But when we tested that against random points scattered on
            Boston's bike network, they scored 94.1% too. The apparent match was an artifact of how densely
            crashes blanket the city's streets, not evidence that people fear the right places. We're reporting
            the non-finding because the check is the point.
          </p>
        </section>

        <section class="map-panel">
          <CrashMap showCrashes={false} showConcerns={true} visible={currentScreen === 7} {concernCallouts} />
        </section>
      </div>
    </section>
  </div>

  <div class="screen-slot" class:visible={currentScreen === 8}>
    <Screen5Closing />
  </div>

  <nav class="pager">
    {#if currentScreen > 0}
      <button class="nav-btn back-btn" on:click={back}>← Back</button>
    {/if}

    <div class="breadcrumb">
      {#each [0, 1, 2, 3, 4, 5, 6, 7, 8] as i}
        <button
          class="stop"
          class:visited={i <= furthestReached}
          class:current={i === currentScreen}
          on:click={() => goTo(i)}
          aria-label="Go to screen {i + 1}"
        >
          {#if i === currentScreen}🚲{/if}
        </button>
        {#if i < LAST_SCREEN}
          <div class="segment" class:filled={i < furthestReached}></div>
        {/if}
      {/each}
    </div>

    {#if currentScreen < LAST_SCREEN}
      <button class="nav-btn next-btn" on:click={next}>Next →</button>
    {/if}
  </nav>
</main>

<style>
  :global(html, body) {
    background: #000;
    height: 100%;
    overflow: hidden;
  }
  main {
    background: #000;
    color: #fff;
    font-family: ui-monospace, 'SFMono-Regular', 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
    height: 100vh;
  }
  .screen-slot {
    display: none;
    height: 100vh;
  }
  .screen-slot.visible {
    display: flex;
    flex-direction: column;
  }
  .screen {
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  /* Unified map-screen heading (2026-08-10): standardized across the
     heatmap screen (Screen2Hero.svelte .headline), THE GAP, and the fear
     map so all three read as one system — values copied 1:1 from
     ScreenMissedCrash.svelte/Screen1Hook.svelte's existing headline
     treatment, since no CSS custom-property/design-token scale exists in
     this project to defer to instead. */
  .screen-eyebrow {
    margin: 0 0 0.6rem;
    font-size: clamp(1.5rem, 3.4vw, 2.3rem);
    font-weight: 600;
    line-height: 1.35;
    color: #fff;
  }
  .data-source-label {
    margin: -0.25rem 0 1.25rem;
    color: #999;
    font-size: 0.78rem;
    line-height: 1.45;
  }
  /* THE GAP-only override (2026-08-10): gray text on this screen bumped to
     white for legibility. Scoped to .explorer-screen specifically, not the
     base .data-source-label rule above, since that class is shared with
     the fear screen, which keeps its original gray. */
  .explorer-screen .data-source-label {
    color: #fff;
  }
  .panels {
    flex: 1;
    display: flex;
    min-height: 0;
  }
  .chart-panel {
    width: 40%;
    padding: 1.5rem;
    padding-bottom: 5rem;
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
    color: #fff;
    font-weight: 600;
  }
  .legend-hint {
    color: #fff;
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
  .swatch-pink {
    background: #e28aab;
  }
  .swatch-blue {
    background: #7fb2e5;
  }
  .swatch-yellow {
    background: #f2d06b;
  }
  .null-model-note {
    margin: 1.5rem 0 0;
    padding-top: 0.85rem;
    border-top: 1px solid #222;
    color: #777;
    font-size: 0.72rem;
    font-style: italic;
    line-height: 1.5;
  }
  .null-model-note strong {
    color: #999;
    font-style: normal;
  }
  /* Navigation: fixed bottom bar shared by all 9 screens. */
  .pager {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    z-index: 100;
    pointer-events: none;
  }
  .nav-btn {
    pointer-events: auto;
    font-family: inherit;
    font-size: 0.85rem;
    background: #111;
    border: 1px solid #444;
    border-radius: 20px;
    color: #fff;
    padding: 0.6rem 1.15rem;
    cursor: pointer;
  }
  .nav-btn:hover {
    border-color: #ff4fa2;
    color: #ff4fa2;
  }
  .breadcrumb {
    pointer-events: auto;
    display: flex;
    align-items: center;
    background: rgba(10, 10, 10, 0.75);
    border-radius: 20px;
    padding: 0.5rem 0.9rem;
  }
  .stop {
    flex: none;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 2px solid #444;
    background: transparent;
    padding: 0;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    line-height: 1;
  }
  .stop.visited {
    border-color: #e28aab;
    background: #e28aab;
  }
  .stop.current {
    width: 20px;
    height: 20px;
    background: #000;
  }
  .segment {
    width: 28px;
    height: 2px;
    background: #444;
  }
  .segment.filled {
    background: #e28aab;
  }
</style>
