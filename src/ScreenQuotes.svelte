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
  const quotes = [
    {
      text: 'I was witness to a cyclist getting doored by a rideshare drop-off passenger.',
      category: 'Bike facilities missing or inadequate',
      place: 'Beacon St',
    },
    {
      text: 'I had to yell out to the SUVs to get them to stop turning.',
      category: 'Failure to yield (turning)',
      place: 'Longwood Ave at Brookline Ave / Riverway',
    },
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
  <p class="framing">Before the data — what people actually wrote</p>

  <div class="quote-grid">
    {#each quotes as q, i}
      <blockquote class="pull-quote offset-{i % 3}">
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
    justify-content: center;
    background: #000;
    padding: 2.5rem 4rem 5.5rem;
    box-sizing: border-box;
    overflow-y: auto;
  }
  .framing {
    margin: 0 0 1.75rem;
    color: #666;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    text-align: center;
    flex: none;
  }
  .quote-grid {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    max-width: 50rem;
    margin: 0 auto;
    width: 100%;
    flex: none;
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
  .pull-quote footer {
    margin-top: 0.5rem;
    color: #777;
    font-size: 0.75rem;
    font-style: normal;
  }
  /* Staggered horizontal offsets so quotes read as distinct voices rather
     than a stacked list. */
  .offset-0 {
    text-align: left;
    padding-right: 15%;
  }
  .offset-1 {
    text-align: right;
    padding-left: 15%;
  }
  .offset-2 {
    text-align: left;
    padding-right: 8%;
    padding-left: 8%;
  }
  .offset-0 p,
  .offset-2 p {
    color: #ff4fa2;
  }
</style>
