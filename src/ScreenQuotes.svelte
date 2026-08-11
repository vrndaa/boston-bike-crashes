<script>
  // Verbatim excerpts from data/safety_concerns.geojson (mode == 'bike').
  // Trimmed to a single short, punchy sentence per the project owner's
  // request — context intentionally dropped in favor of impact. Nothing
  // reworded; typos in source text (e.g. "experieence") kept as-is. One
  // quote (Main St) is trimmed to start mid-sentence — its first letter is
  // capitalized for display, a typographic convention, not a wording change.
  // Two of the longest submitted comments described an actual pedestrian
  // death and were deliberately excluded — CLAUDE.md scopes individual
  // crash/fatality callouts as Phase 2, out of scope until asked for
  // directly.
  //
  // Narrowed 2026-08-11 from six quotes to these four, each re-verified as
  // the sole match for its distinctive phrase against the full comment
  // text in public/data/safety_concerns.geojson (one match apiece, no
  // ambiguity to resolve).
  const quotes = [
    {
      text: 'Some of these crossings can be very dangerous as past accidents and close calls show.',
      category: 'Failure to yield (going straight)',
      place: 'SW Corridor path at New Minton St',
    },
    {
      text: 'I cross this intersection on a bike daily and see/experieence car-and-bike near misses often.',
      category: 'Other (bike lane signage)',
      place: 'Poplar St / Florence St',
    },
    {
      text: "A driver “laid on their horn” and physically threatened me by driving immediately behind my rear tire.",
      category: 'Bike facilities missing or inadequate',
      place: 'Main St',
    },
    {
      text: 'Every. Single. Time that I walk or bike down this street, the lanes are completely blocked with multiple drivers stopped.',
      category: 'Bike facilities missing or inadequate',
      place: 'Cambridge St near MGH',
    },
  ];
</script>

<section class="quotes-screen">
  <div class="quote-grid">
    {#each quotes as q, i}
      <blockquote class="pull-quote offset-{i % 2}">
        <p>&ldquo;{q.text}&rdquo;</p>
        <footer>{q.category} &middot; {q.place}</footer>
      </blockquote>
    {/each}
  </div>
</section>

<style>
  .quotes-screen {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #000;
    padding: 2.5rem 4rem 5.5rem;
    box-sizing: border-box;
    overflow-y: auto;
  }
  /* Balanced vertical distribution (2026-08-11): the grid now claims the
     full remaining screen height and spaces its four quotes evenly across
     it (space-evenly, not space-between, so there's breathing room above
     the first quote and below the last too) instead of collapsing to a
     centered cluster. */
  .quote-grid {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    max-width: 50rem;
    margin: 0 auto;
    width: 100%;
  }
  .pull-quote {
    margin: 0;
  }
  .pull-quote p {
    margin: 0;
    color: #fff;
    font-size: 1.3rem;
    font-weight: 600;
    line-height: 1.4;
  }
  /* Source line in the same full-strength Chapter 2 green used everywhere
     else in this chapter (bars, dots, concern-map chrome) — no softening
     this time, per instruction. */
  .pull-quote footer {
    margin-top: 0.5rem;
    color: var(--color-chapter2);
    font-size: 0.75rem;
    font-style: normal;
  }
  /* Strict left/right/left/right alternation (2026-08-11) — each quote
     on the opposite side from the one before it. */
  .offset-0 {
    text-align: left;
    padding-right: 15%;
  }
  .offset-1 {
    text-align: right;
    padding-left: 15%;
  }
</style>
