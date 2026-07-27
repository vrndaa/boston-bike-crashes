<script>
  import { onMount } from 'svelte';

  let categories = [];
  let otherDetails = [];
  let loadError = null;

  const CATEGORIES_URL = `${import.meta.env.BASE_URL}data/concern_categories_bike.json`;
  const CONCERNS_URL = `${import.meta.env.BASE_URL}data/safety_concerns.geojson`;

  onMount(async () => {
    try {
      const [catRes, concernsRes] = await Promise.all([fetch(CATEGORIES_URL), fetch(CONCERNS_URL)]);
      if (!catRes.ok || !concernsRes.ok) throw new Error('failed to load concern category data');

      // File already sorted descending by count — used as-is, no recoding.
      categories = await catRes.json();

      // Raw request_other text, for the "Other" bar's expanded tooltip only.
      const geojson = await concernsRes.json();
      otherDetails = geojson.features
        .map((f) => f.properties)
        .filter((p) => p.mode === 'bike' && p.request === 'other' && p.request_other)
        .map((p) => p.request_other);
    } catch (e) {
      loadError = e.message;
      console.warn('Could not load concern category data:', e.message);
    }
  });

  $: maxCount = categories.length ? Math.max(...categories.map((c) => c.count)) : 1;
</script>

{#if loadError}
  <p class="error">Couldn't load concern categories: {loadError}</p>
{:else if categories.length}
  <div class="concern-chart">
    <h4>Bike safety-concern categories</h4>
    {#each categories as c}
      <button type="button" class="bar-row" aria-label="{c.category}: {c.count} reports">
        <div class="bar-label">{c.category}</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: {(c.count / maxCount) * 100}%"></div>
        </div>
        <div class="bar-count">{c.count}</div>

        {#if c.code === 'other'}
          <div class="bar-tooltip bar-tooltip-list">
            <div class="tooltip-title">Other — {otherDetails.length} raw submissions</div>
            <ul>
              {#each otherDetails as detail}
                <li>{detail}</li>
              {/each}
            </ul>
          </div>
        {:else}
          <div class="bar-tooltip">
            <div class="tooltip-title">{c.category}</div>
            <div>{c.count} reports</div>
          </div>
        {/if}
      </button>
    {/each}
  </div>
{/if}

<style>
  .concern-chart {
    margin-top: 1rem;
  }
  .concern-chart h4 {
    margin: 0 0 0.5rem;
    font-size: 0.85rem;
    color: #ccc;
    font-weight: 600;
  }
  .error {
    color: #ff6b6b;
    font-size: 0.85rem;
  }
  .bar-row {
    position: relative;
    display: grid;
    grid-template-columns: 42% 1fr auto;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
    padding: 0.5rem 0;
    margin: 0;
    background: none;
    border: none;
    color: inherit;
    font-family: inherit;
    text-align: left;
    cursor: default;
  }
  .bar-row:focus-visible {
    outline: 1px solid #BFDD97;
    border-radius: 4px;
  }
  .bar-label {
    font-size: 0.6rem;
    color: #ddd;
    line-height: 1.2;
  }
  .bar-track {
    height: 10px;
    background: #1a1a1a;
    border-radius: 2px;
    overflow: hidden;
  }
  .bar-fill {
    height: 100%;
    background: #BFDD97;
    border-radius: 2px;
  }
  .bar-count {
    font-size: 0.72rem;
    color: #BFDD97;
    font-variant-numeric: tabular-nums;
    text-align: right;
    min-width: 1.5em;
  }

  /* Tooltip: CSS-hover reveal, no JS positioning needed. Anchored to the
     row so it doesn't shift as bars vary in height. */
  .bar-tooltip {
    position: absolute;
    left: 0;
    top: 100%;
    z-index: 10;
    margin-top: 4px;
    background: #1a1408;
    border: 1px solid #BFDD97;
    border-radius: 6px;
    padding: 0.5rem 0.6rem;
    font-size: 0.72rem;
    color: #f2f2f2;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.1s;
    white-space: nowrap;
  }
  .bar-row:hover .bar-tooltip,
  .bar-row:focus .bar-tooltip,
  .bar-row:focus-visible .bar-tooltip {
    opacity: 1;
  }
  .tooltip-title {
    font-weight: 600;
    color: #BFDD97;
    margin-bottom: 0.25rem;
  }

  /* "Other" gets a taller, scrollable list instead of a one-liner — capped
     so 13 short strings don't turn into a giant overflow blob. Needs its
     own pointer-events: the base .bar-tooltip disables them (plain
     tooltips don't need hover), but this one must catch the mouse to be
     scrollable. It's still a DOM descendant of the button, so hovering
     into it doesn't break the button's :hover that keeps it visible. */
  .bar-tooltip-list {
    white-space: normal;
    width: 260px;
    max-height: 160px;
    overflow-y: auto;
    pointer-events: auto;
  }
  .bar-tooltip-list ul {
    margin: 0;
    padding-left: 1rem;
  }
  .bar-tooltip-list li {
    margin-bottom: 0.3rem;
    line-height: 1.3;
    color: #ddd;
  }
</style>
