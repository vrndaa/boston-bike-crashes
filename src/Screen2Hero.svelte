<script>
  import HeroMap from './HeroMap.svelte';

  export let visible = true;

  let cardVisible = true;
</script>

<section class="hero">
  <HeroMap {visible} />

  <p class="tech-credential">MAPLIBRE GL · GEOJSON · 4,236 CRASHES</p>

  {#if cardVisible}
    <div class="stat-card">
      <button class="close-btn" on:click={() => (cardVisible = false)} aria-label="Close">×</button>
      <h1>What Boston Doesn't Know About Bike Crashes</h1>
      <p class="subtitle">Two government systems track the same crashes. They rarely agree.</p>

      <div class="stats">
        <div class="stat">
          <div class="stat-number" style="color: #e28aab">12%</div>
          <div class="stat-label">confirmed by both sources</div>
        </div>
        <div class="stat">
          <div class="stat-number" style="color: #7fb2e5">74%</div>
          <div class="stat-label">911 dispatch only</div>
        </div>
        <div class="stat">
          <div class="stat-number" style="color: #f2d06b">14%</div>
          <div class="stat-label">police report only</div>
        </div>
      </div>

      <p class="methodology">
        A crash counts as "confirmed" only if it appears in both Boston's 911 dispatch log and the state's
        police crash database, matched within 2 hours and 100 meters.
      </p>

      <p class="hint">Click any dot for crash detail. Drag the chart to filter by date. Next screen: what people fear.</p>
    </div>
  {/if}
</section>

<style>
  .hero {
    position: relative;
    min-height: 100vh;
    background: #000;
    overflow: hidden;
  }
  .hero :global(.hero-map) {
    position: absolute;
    inset: 0;
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
  .stat-card {
    position: absolute;
    top: 1.25rem;
    right: 1.25rem;
    z-index: 2;
    max-width: 19rem;
    background: rgba(10, 10, 10, 0.88);
    border: 1px solid #333;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    backdrop-filter: blur(4px);
  }
  .close-btn {
    position: absolute;
    top: 0.6rem;
    right: 0.75rem;
    background: none;
    border: none;
    color: #777;
    font-size: 1.2rem;
    line-height: 1;
    cursor: pointer;
    padding: 0.25rem;
  }
  .close-btn:hover {
    color: #fff;
  }
  h1 {
    margin: 0;
    font-size: 1rem;
    color: #fff;
  }
  .subtitle {
    margin: 0.35rem 0 0;
    color: #aaa;
    font-size: 0.78rem;
  }
  .stats {
    display: flex;
    gap: 1rem;
    margin: 0.9rem 0;
  }
  .stat-number {
    font-size: 1.4rem;
    font-weight: 700;
    line-height: 1;
  }
  .stat-label {
    margin-top: 0.25rem;
    color: #999;
    font-size: 0.62rem;
    line-height: 1.25;
  }
  .methodology {
    margin: 0 0 0.6rem;
    color: #888;
    font-size: 0.66rem;
    font-style: italic;
    line-height: 1.4;
  }
  .hint {
    margin: 0;
    color: #666;
    font-size: 0.66rem;
    line-height: 1.35;
    border-top: 1px solid #2a2a2a;
    padding-top: 0.5rem;
  }
</style>
