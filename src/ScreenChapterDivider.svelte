<script>
  // Reusable text-only "breather" screen — used for both Chapter 1 and
  // Chapter 2 dividers. Styling copied 1:1 from Screen1Hook.svelte (same
  // full-viewport dark background, same centered large-bold headline
  // treatment) since both dividers serve the same function as that screen.
  export let text = '';
  export let chapterLabel = ''; // e.g. "Chapter One" — rendered uppercase via CSS
  export let labelColor = '#fff'; // caller passes the color per chapter
</script>

<section class="chapter-divider">
  <div class="chapter-content">
    {#if chapterLabel}
      <p class="chapter-label" style="color: {labelColor}">{chapterLabel}</p>
    {/if}
    <h2>{text}</h2>
  </div>
</section>

<style>
  .chapter-divider {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #000;
    padding: 2rem;
    box-sizing: border-box;
  }
  .chapter-content {
    max-width: 46rem;
    text-align: center;
  }
  .chapter-label {
    margin: 0 0 0.85rem;
    font-size: 0.95rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
  }
  h2 {
    margin: 0;
    font-size: clamp(1.6rem, 4vw, 2.8rem);
    font-weight: 600;
    line-height: 1.35;
    color: #fff;
  }
</style>
