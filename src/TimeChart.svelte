<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  export let selectedRange = null; // bound from parent; brushing here updates it

  let container;
  let recordCount = null;
  let loadError = null;
  let chartData = null;
  let showRollingAvg = false;

  const CRASH_DATA_URL = '/data/boston_bike_crashes.geojson';

  // Policy/infrastructure context, shown as passive chart annotations (not
  // clickable — see CLAUDE.md Phase 1 scope). Dates confirmed against
  // CLAUDE.md's decision log, not asserted from memory.
  const annotations = [
    { type: 'line', date: '2017-01-09', label: 'Speed limit 30→25 mph' },
    { type: 'band', start: '2020-03-01', end: '2020-06-01', label: 'COVID ridership dip' },
  ];

  // Trailing rolling average — each point averages itself plus up to two
  // prior months, so early months use a partial window instead of needing
  // data outside the plotted range.
  function rollingAverage(data, window = 3) {
    return data.map((d, i) => {
      const start = Math.max(0, i - window + 1);
      const slice = data.slice(start, i + 1);
      return { date: d.date, avg: d3.mean(slice, (s) => s.count) };
    });
  }

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

  function draw(data, showAvg) {
    container.innerHTML = '';
    const width = container.clientWidth;
    // Wider-than-tall on purpose: a shallower aspect ratio flattens peak
    // steepness through geometry alone, without touching the underlying
    // counts.
    const height = 180;
    const margin = { top: 24, right: 10, bottom: 30, left: 35 };

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

    // Annotation bands drawn first so they sit behind the crash data.
    for (const a of annotations) {
      if (a.type !== 'band') continue;
      svg
        .append('rect')
        .attr('x', x(new Date(a.start)))
        .attr('width', x(new Date(a.end)) - x(new Date(a.start)))
        .attr('y', margin.top)
        .attr('height', height - margin.top - margin.bottom)
        .attr('fill', '#ffffff')
        .attr('opacity', 0.06)
        .attr('stroke', '#888')
        .attr('stroke-dasharray', '3,3')
        .attr('stroke-width', 1);
    }

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

    if (showAvg) {
      const avgData = rollingAverage(data, 3);
      const avgLine = d3
        .line()
        .x((d) => x(d.date))
        .y((d) => y(d.avg));

      svg
        .append('path')
        .datum(avgData)
        .attr('fill', 'none')
        .attr('stroke', '#8fe3ff')
        .attr('stroke-width', 2)
        .attr('d', avgLine);

      svg
        .append('text')
        .attr('x', width - margin.right)
        .attr('y', margin.top - 8)
        .attr('text-anchor', 'end')
        .attr('fill', '#8fe3ff')
        .attr('font-size', 11)
        .text('3-month average');
    }

    // Annotation lines/labels drawn on top so they stay legible against
    // both the raw area and the average line.
    for (const a of annotations) {
      if (a.type !== 'line') continue;
      const lineX = x(new Date(a.date));
      svg
        .append('line')
        .attr('x1', lineX)
        .attr('x2', lineX)
        .attr('y1', margin.top)
        .attr('y2', height - margin.bottom)
        .attr('stroke', '#888')
        .attr('stroke-dasharray', '3,3')
        .attr('stroke-width', 1);
      svg
        .append('text')
        .attr('x', lineX + 4)
        .attr('y', margin.top - 8)
        .attr('fill', '#aaa')
        .attr('font-size', 10)
        .text(a.label);
    }
    for (const a of annotations) {
      if (a.type !== 'band') continue;
      svg
        .append('text')
        .attr('x', x(new Date(a.start)) + 4)
        .attr('y', margin.top - 8)
        .attr('fill', '#aaa')
        .attr('font-size', 10)
        .text(a.label);
    }

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
      chartData = monthlyCounts(geojson.features);
    } catch (e) {
      loadError = e.message;
      console.warn('Could not load crash data for chart:', e.message);
    }
  });

  // Redraws whenever the data first arrives or the rolling-average toggle
  // flips. showRollingAvg is referenced directly here (not just inside
  // draw) so Svelte tracks it as a dependency.
  $: if (container && chartData) {
    draw(chartData, showRollingAvg);
  }
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
  <label class="avg-toggle">
    <input type="checkbox" bind:checked={showRollingAvg} />
    Show 3-month average
  </label>
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
  .avg-toggle {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin: 0 0 0.5rem;
    color: #8fe3ff;
    font-size: 0.82rem;
    cursor: pointer;
  }
</style>
