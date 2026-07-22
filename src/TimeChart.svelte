<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  export let selectedRange = null; // bound from parent; brushing here updates it

  let container;

  // TODO (Phase 1, step 1 & 3): replace with real monthly crash counts
  // loaded from data/boston_bike_crashes.geojson (see scripts/fetch_crash_data.py).
  // Placeholder: monthly counts, 2015-01 through 2025-12, synthetic values
  // ONLY so the chart+brush mechanic can be built and tested before real
  // data lands. Do not present these numbers as real in any UI copy.
  function placeholderData() {
    const months = d3.timeMonths(new Date(2015, 0, 1), new Date(2026, 0, 1));
    return months.map((date) => ({
      date,
      count: 15 + Math.round(10 * Math.sin(date.getMonth() / 2) + Math.random() * 8),
    }));
  }

  onMount(() => {
    const data = placeholderData();
    const width = container.clientWidth;
    const height = 260;
    const margin = { top: 20, right: 10, bottom: 30, left: 35 };

    const svg = d3
      .select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const x = d3
      .scaleTime()
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
      .attr('fill', '#c9ada7')
      .attr('opacity', 0.8)
      .attr('d', area);

    svg
      .append('g')
      .attr('transform', `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x).ticks(width / 80));

    svg.append('g').attr('transform', `translate(${margin.left},0)`).call(d3.axisLeft(y).ticks(5));

    // Brush: this is the core mechanic. Selecting a range here should
    // update `selectedRange`, which the parent passes down to CrashMap.
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
  });
</script>

<div class="chart">
  <h3>Bike crashes over time <span class="note">(placeholder data — see TODO)</span></h3>
  <p class="hint">Drag on the chart to select a date range and filter the map.</p>
  <div bind:this={container}></div>
</div>

<style>
  .chart h3 {
    margin: 0 0 0.25rem;
    font-size: 1rem;
  }
  .note {
    font-weight: 400;
    color: #b33;
    font-size: 0.8rem;
  }
  .hint {
    margin: 0 0 0.5rem;
    color: #666;
    font-size: 0.85rem;
  }
</style>
