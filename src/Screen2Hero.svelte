<script>
  import HeroMap from './HeroMap.svelte';

  export let visible = true;
</script>

<section class="screen hero-screen">
  <div class="panels">
    <section class="chart-panel">
      <h2 class="headline">What Boston Doesn't Know About Bike Crashes</h2>
      <p class="subtitle">Two government systems track the same crashes. They rarely agree.</p>

      <div class="stat-legend">
        <div class="stat-row">
          <span class="stat-dot swatch-pink"></span>
          <span class="stat-number" style="color: #e28aab">12%</span>
          <span class="stat-label">confirmed by both sources</span>
        </div>
        <div class="stat-row">
          <span class="stat-dot swatch-blue"></span>
          <span class="stat-number" style="color: #7fb2e5">74%</span>
          <span class="stat-label">911 dispatch only</span>
        </div>
        <div class="stat-row">
          <span class="stat-dot swatch-yellow"></span>
          <span class="stat-number" style="color: #f2d06b">14%</span>
          <span class="stat-label">police report only</span>
        </div>
      </div>

      <p class="methodology">
        A crash counts as "confirmed" only if it appears in both Boston's 911 dispatch log and the state's
        police crash database, matched within 2 hours and 100 meters.
      </p>
    </section>

    <section class="map-panel">
      <p class="tech-credential">MAPLIBRE GL · GEOJSON · 4,236 CRASHES</p>
      <HeroMap {visible} />
    </section>
  </div>
</section>

<style>
  /* Layout structure mirrors the explorer ("The Gap") screen's .screen /
     .panels / .chart-panel / .map-panel split in App.svelte — duplicated
     here rather than shared, since Svelte scopes each component's <style>
     block to its own template and can't reach into a sibling component's
     markup. Values are copied 1:1 so the two screens read as one system. */
  .screen {
    height: 100vh;
    display: flex;
    flex-direction: column;
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
    position: relative;
    flex: 1;
  }
  .headline {
    margin: 0 0 0.6rem;
    font-size: clamp(1.5rem, 3.4vw, 2.3rem);
    font-weight: 600;
    line-height: 1.35;
    color: #fff;
  }
  .subtitle {
    margin: 0 0 1.75rem;
    color: #999;
    font-size: 0.85rem;
    line-height: 1.5;
  }
  .stat-legend {
    display: flex;
    flex-direction: column;
    gap: 1.15rem;
    margin: 0 0 1.75rem;
  }
  .stat-row {
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
  }
  .stat-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    flex: none;
    align-self: center;
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
  .stat-number {
    font-size: 2.6rem;
    font-weight: 700;
    line-height: 1;
    font-variant-numeric: tabular-nums;
  }
  .stat-label {
    color: #ccc;
    font-size: 0.9rem;
  }
  .methodology {
    margin: 0;
    color: #888;
    font-size: 0.75rem;
    font-style: italic;
    line-height: 1.5;
  }
  .tech-credential {
    position: absolute;
    top: 1.25rem;
    left: 1.5rem;
    margin: 0;
    color: #777;
    font-size: 0.7rem;
    letter-spacing: 0.05em;
    z-index: 2;
  }
</style>
