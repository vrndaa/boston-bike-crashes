<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  export let selectedRange = null; // bound from parent; brushing here updates it
  // Button/breadcrumb nav keeps every screen mounted, just hidden via CSS.
  // draw() measures container.clientWidth, which reads 0 while hidden —
  // same underlying issue as the map components' resize prop, different
  // fix since this is an SVG chart, not MapLibre: redraw once visible.
  export let visible = true;

  let container;
  let loadError = null;
  let chartData = null;

  const CRASH_DATA_URL = '/data/boston_bike_crashes.geojson';
  // 2021-01-01: matches the MassDOT comparison window shown on the map
  // (see match_crashes.py — pre_massdot cutoff). Chart is windowed to the
  // same start so the two views cover identical time spans. This does set
  // aside real 2015–2020 Vision Zero data that exists in the source file —
  // an intentional scope decision for this screen, not a data gap.
  const CHART_START = new Date('2021-01-01T00:00:00Z');

  // Group real crash features into monthly counts. Every number here comes
  // straight from the downloaded GeoJSON — no synthetic/estimated values.
  // Bucketed in UTC (d3.utcMonth, not d3.timeMonth) because dispatch_ts/
  // timestamp_ms are stored in UTC — bucketing in the viewer's local
  // timezone would shift ~0.5% of records across month boundaries.
  function monthlyCounts(features) {
    const dates = features
      .map((f) => f.properties && f.properties.timestamp_ms)
      .filter((ms) => typeof ms === 'number')
      .map((ms) => new Date(ms))
      .filter((d) => d >= CHART_START);

    const [minDate, maxDate] = d3.extent(dates);
    const firstMonth = d3.utcMonth.floor(minDate);
    const lastMonth = d3.utcMonth.floor(maxDate);

    const countsByMonth = d3.rollup(
      dates,
      (v) => v.length,
      (d) => +d3.utcMonth.floor(d)
    );

    // Fill every month in range, including zero-count months, so gaps show
    // as real dips rather than being skipped over.
    const months = d3.utcMonths(firstMonth, d3.utcMonth.offset(lastMonth, 1));
    return months.map((date) => ({
      date,
      count: countsByMonth.get(+date) || 0,
    }));
  }

  function draw(data) {
    container.innerHTML = '';
    const width = container.clientWidth;
    // Wider-than-tall on purpose: a shallower aspect ratio flattens peak
    // steepness through geometry alone, without touching the underlying
    // counts. Bottom margin sized so year tick labels aren't cramped
    // against the chart body.
    const height = 220;
    const margin = { top: 24, right: 10, bottom: 44, left: 35 };

    const svg = d3
      .select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    // UTC scale to match the UTC bucketing above — tick labels line up
    // exactly with the month boundaries the data was grouped on.
    const x = d3
      .scaleUtc()
      .domain(d3.extent(data, (d) => d.date))
      .range([margin.left, width - margin.right]);

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d) => d.count)])
      .nice()
      .range([height - margin.bottom, margin.top]);

    const area = d3
      .area()
      .x((d) => x(d.date))
      .y0(y(0))
      .y1((d) => y(d.count));

    svg
      .append('path')
      .datum(data)
      .attr('fill', '#ff4fa2')
      .attr('opacity', 0.85)
      .attr('d', area);

    const xAxis = svg
      .append('g')
      .attr('transform', `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x).ticks(width / 80));

    const yAxis = svg
      .append('g')
      .attr('transform', `translate(${margin.left},0)`)
      .call(d3.axisLeft(y).ticks(5));

    for (const axis of [xAxis, yAxis]) {
      axis.selectAll('text').attr('fill', '#f2f2f2');
      axis.selectAll('path, line').attr('stroke', '#888');
    }

    // Brush: this is the core mechanic. Selecting a range here updates
    // `selectedRange`, which the parent passes down to CrashMap to filter
    // the map's crash-points layer live.
    const brush = d3
      .brushX()
      .extent([
        [margin.left, margin.top],
        [width - margin.right, height - margin.bottom],
      ])
      .on('end', (event) => {
        if (!event.selection) {
          selectedRange = null;
          return;
        }
        const [x0, x1] = event.selection.map(x.invert);
        selectedRange = { start: x0, end: x1 };
      });

    svg.append('g').attr('class', 'brush').call(brush);
  }

  onMount(async () => {
    try {
      const res = await fetch(CRASH_DATA_URL);
      if (!res.ok) throw new Error(`fetch failed: ${res.status}`);
      const geojson = await res.json();
      chartData = monthlyCounts(geojson.features);
    } catch (e) {
      loadError = e.message;
      console.warn('Could not load crash data for chart:', e.message);
    }
  });

  // Redraws whenever the data first arrives, or whenever this screen
  // becomes visible again — container.clientWidth is 0 while hidden, so a
  // draw that happened while off-screen needs to be redone once shown.
  $: if (container && chartData && visible) {
    draw(chartData);
  }
</script>

<div class="chart">
  <h3>Bike crashes over time</h3>
  <p class="hint">Drag on the chart to select a date range and filter the map. Showing 2021–present.</p>
  {#if loadError}
    <p class="error">Couldn't load crash data: {loadError}</p>
  {:else if !chartData}
    <p class="hint">Loading real crash data…</p>
  {/if}
  <div bind:this={container}></div>
</div>

<style>
  .chart h3 {
    margin: 0 0 0.25rem;
    font-size: 1rem;
  }
  .hint {
    margin: 0 0 0.5rem;
    color: #aaa;
    font-size: 0.85rem;
  }
  .error {
    margin: 0 0 0.5rem;
    color: #ff6b6b;
    font-size: 0.85rem;
  }
</style>
