<section class="closing">
  <div class="closing-content">
    <p>
      No one looking at Boston's bike crashes right now knows where to look first. The city keeps two counts
      and no shared picture between them, and neither one holds the near-misses, the dread, or the corridors
      residents name again and again. <span class="accent">What's missing isn't a better database. It's one
      record that reconciles what both systems already logged and counts residents' concerns beside it</span>,
      so that anyone deciding where to act can finally see the full intensity of what's happening on these
      streets.
    </p>
    <p>
      <span class="accent">So the harm isn't just that the number's too low.</span> It's that decisions about
      which streets get lanes, signals, and money run on the broken, lagging tally, while the residents naming
      the same corridors over and over get <span class="accent">treated as noise instead of the leading signal
      they are.</span>
    </p>
    <p>
      If you're using official crash data to judge whether a street is safe, <span class="accent">you're seeing
      a fraction of what actually happened there.</span>
    </p>
    <p class="credit">
      Matching methodology: a dispatch report and a police crash report are counted as the same incident when
      they fall within 2 hours and 100 meters of each other — a proximity-matching approach similar to the one
      BCU Labs (Boston Cyclists Union, built with BU Spark!) uses to compare MassDOT and Boston Vision Zero
      crash data. Sources: City of Boston Vision Zero · MassDOT IMPACT · Boston Vision Zero Safety Concerns.
    </p>
  </div>
</section>

<style>
  .closing {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #000;
    padding: 2rem;
    box-sizing: border-box;
  }
  .closing-content {
    max-width: 38rem;
  }
  .closing-content p {
    color: #ccc;
    font-size: 1.05rem;
    line-height: 1.6;
    margin: 0 0 1.25rem;
  }
  /* Same hot pink as Screen1Hook's .accent ("They rarely agree.") — reused
     verbatim (#ff4fa2), not a new value. */
  .accent {
    color: #ff4fa2;
  }
  .closing-content p.credit {
    margin-top: 1.75rem;
    color: #555;
    font-size: 0.6rem;
    font-style: italic;
    line-height: 1.4;
  }
</style>
