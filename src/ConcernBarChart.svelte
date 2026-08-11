<script>
  import { onMount } from 'svelte';

  // Explicit, auditable grouping of the 14 leaf categories in
  // data/concern_categories_bike.json into 4 display groups. Codes must
  // match that file's `code` values exactly (see
  // scripts/build_concern_categories.py for where those codes come from).
  // "Other" is always rendered last, regardless of its total.
  const GROUPS = [
    { label: 'Driver behavior', codes: ['yieldturn', 'doublepark', 'runlightssigns', 'yieldgoing', 'speeding'] },
    { label: 'Road conditions', codes: ['roadwaymaint', 'sidewalk', 'visibility', 'toomanylanes'] },
    { label: 'Crossing and signal timing', codes: ['walksignal', 'notenoughtime', 'awayfromside'] },
    { label: 'Other', codes: ['other'] },
  ];

  let categories = [];
  let otherDetails = [];
  let bikefacilityCommentCount = 0;
  let loadError = null;

  const CATEGORIES_URL = `${import.meta.env.BASE_URL}data/concern_categories_bike.json`;
  const CONCERNS_URL = `${import.meta.env.BASE_URL}data/safety_concerns.geojson`;

  onMount(async () => {
    try {
      const [catRes, concernsRes] = await Promise.all([fetch(CATEGORIES_URL), fetch(CONCERNS_URL)]);
      if (!catRes.ok || !concernsRes.ok) throw new Error('failed to load concern category data');

      // File already sorted descending by count — used as-is, no recoding.
      categories = await catRes.json();

      const geojson = await concernsRes.json();
      const bikeProps = geojson.features.map((f) => f.properties).filter((p) => p.mode === 'bike');

      // Raw request_other text, for the "Other" bar's expanded tooltip only.
      otherDetails = bikeProps.filter((p) => p.request === 'other' && p.request_other).map((p) => p.request_other);

      // Fill rate for the pull-quote sub-line — counted from the same fetch,
      // not a hardcoded number.
      bikefacilityCommentCount = bikeProps.filter((p) => p.request === 'bikefacility' && p.comments).length;
    } catch (e) {
      loadError = e.message;
      console.warn('Could not load concern category data:', e.message);
    }
  });

  // Single shared scale for the bikefacility bar and all four group bars.
  // The anchor is read from the data file (currently 92), never a literal.
  $: bikefacility = categories.find((c) => c.code === 'bikefacility');
  $: maxCount = bikefacility ? bikefacility.count : 1;

  // Every group total is summed from the data file's own counts at runtime —
  // never a hardcoded literal.
  $: groups = GROUPS.map((g) => {
    const subs = g.codes.map((code) => categories.find((c) => c.code === code)).filter(Boolean);
    const total = subs.reduce((sum, c) => sum + c.count, 0);
    return { ...g, subs, total };
  });
</script>

{#if loadError}
  <p class="error">Couldn't load concern categories: {loadError}</p>
{:else if categories.length && bikefacility}
  <div class="concern-chart">
    <p class="section-label">Largest single category</p>

    <button type="button" class="bar-row bar-row-solo" aria-label="{bikefacility.category}: {bikefacility.count} reports">
      <div class="bar-label">{bikefacility.category}</div>
      <div class="bar-track">
        <div class="bar-fill" style="width: {(bikefacility.count / maxCount) * 100}%"></div>
      </div>
      <div class="bar-count">{bikefacility.count}</div>
    </button>

    <blockquote class="pull-quote">
      <p>Half of what cyclists report isn't a driver. It's a missing bike lane.</p>
      <footer>{bikefacilityCommentCount} of those {bikefacility.count} wrote out why in their own words.</footer>
    </blockquote>

    <p class="section-label">Everything else, grouped</p>

    {#each groups as g}
      <button type="button" class="bar-row" aria-label="{g.label}: {g.total} reports">
        <div class="bar-label">{g.label}</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: {(g.total / maxCount) * 100}%"></div>
        </div>
        <div class="bar-count">{g.total}</div>

        {#if g.label === 'Other'}
          <div class="bar-tooltip bar-tooltip-list">
            <div class="tooltip-title">Other — {otherDetails.length} raw submissions</div>
            <ul>
              {#each otherDetails as detail}
                <li>{detail}</li>
              {/each}
            </ul>
          </div>
        {:else}
          <div class="bar-tooltip bar-tooltip-list">
            <div class="tooltip-title">{g.label}</div>
            <ul>
              {#each g.subs as s}
                <li>{s.category} — {s.count}</li>
              {/each}
            </ul>
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
  .error {
    color: #ff6b6b;
    font-size: 0.85rem;
  }
  .section-label {
    margin: 1.1rem 0 0.5rem;
    color: #777;
    font-size: 0.62rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  .section-label:first-child {
    margin-top: 0;
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
    outline: 1px solid var(--color-chapter2);
    border-radius: 4px;
  }
  .bar-label {
    font-size: 0.6rem;
    color: #ddd;
    line-height: 1.2;
  }
  .bar-row-solo .bar-label {
    font-size: 0.68rem;
    color: #f2f2f2;
  }
  .bar-track {
    height: 10px;
    background: #1a1a1a;
    border-radius: 2px;
    overflow: hidden;
  }
  .bar-fill {
    height: 100%;
    background: var(--color-chapter2);
    border-radius: 2px;
  }
  .bar-count {
    font-size: 0.72rem;
    color: var(--color-chapter2);
    font-variant-numeric: tabular-nums;
    text-align: right;
    min-width: 1.5em;
  }

  /* Pull quote: left-accent border in the bar color, sits between the
     solo bikefacility bar and the grouped bars below it. */
  .pull-quote {
    margin: 0.85rem 0 0.25rem;
    padding: 0.5rem 0 0.5rem 0.9rem;
    border-left: 3px solid var(--color-chapter2);
  }
  .pull-quote p {
    margin: 0;
    color: #f2f2f2;
    font-size: 0.95rem;
    font-weight: 600;
    line-height: 1.4;
  }
  .pull-quote footer {
    margin-top: 0.35rem;
    color: #999;
    font-size: 0.72rem;
    font-style: normal;
  }

  /* Tooltip: CSS-hover/focus reveal, no JS positioning needed. Anchored to
     the row so it doesn't shift as bars vary in height. Keyboard-reachable
     via :focus-visible on the button, same mechanism as the click-to-filter
     legend elsewhere in the app. */
  .bar-tooltip {
    position: absolute;
    left: 0;
    top: 100%;
    z-index: 10;
    margin-top: 4px;
    background: #1a1408;
    border: 1px solid var(--color-chapter2);
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
    color: var(--color-chapter2);
    margin-bottom: 0.25rem;
  }

  /* Taller, scrollable list instead of a one-liner — capped so a long
     sub-category or raw-string list doesn't turn into a giant overflow
     blob. Needs its own pointer-events: the base .bar-tooltip disables
     them (plain tooltips don't need hover), but this one must catch the
     mouse to be scrollable. It's still a DOM descendant of the button, so
     hovering into it doesn't break the button's :hover that keeps it
     visible. */
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
