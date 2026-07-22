<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  export let selectedRange = null; // bound from parent; brushing here updates it

  let container;
  let recordCount = null;
  let loadError = null;

  const CRASH_DATA_URL = '/data/boston_bike_crashes.geojson';

  // Group real crash features into monthly counts. Every number here comes
  // straight from the downloaded GeoJSON — no synthetic/estimated values.
  // Bucketed in UTC (d3.utcMonth, not d3.timeMonth) because dispatch_ts/
  // timestamp_ms are stored in UTC — bucketing in the viewer's local
  // timezone would shift ~0.5% of records across month boundaries.
  function monthlyCounts(features) {
    const dates = features
      .map((f) => f.properties && f.properties.timestamp_ms)
      .filter((ms) => typeof ms === 'number')
      .map((ms) => new Date(ms));

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
    const height = 260;
    const margin = { top: 20, right: 10, bottom: 30, left: 35 };

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
      recordCount = geojson.features.length;
      const data = monthlyCounts(geojson.features);
      draw(data);
    } catch (e) {
      loadError = e.message;
      console.warn('Could not load crash data for chart:', e.message);
    }
  });
</script>

<div class="chart">
  <h3>Bike crashes over time</h3>
  <p class="hint">Drag on the chart to select a date range and filter the map.</p>
  {#if recordCount !== null}
    <p class="count">Count of records: {recordCount.toLocaleString()} reported bike crashes, Jan 2015–present</p>
  {:else if loadError}
    <p class="error">Couldn't load crash data: {loadError}</p>
  {:else}
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
  .count {
    margin: 0 0 0.5rem;
    color: #ccc;
    font-size: 0.8rem;
    font-variant-numeric: tabular-nums;
  }
  .error {
    margin: 0 0 0.5rem;
    color: #ff6b6b;
    font-size: 0.85rem;
  }
</style>
