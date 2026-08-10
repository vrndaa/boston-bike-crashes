<script>
  import { onMount, onDestroy } from 'svelte';

  // Screen 2's full-bleed background map: a static, non-interactive backdrop
  // showing every matched crash (both/vz_only/massdot_only — pre_massdot
  // excluded, same scope as "The Gap" explorer). No brush, no click, no
  // hover — just the picture behind the stat card. Muted palette per
  // 2026-07-26 decision, distinct from the brighter Screen 3 colors.
  const CRASH_DATA_URL = `${import.meta.env.BASE_URL}data/boston_bike_crashes_enriched.geojson`;

  // See CrashMap.svelte's identical prop for why this exists: with
  // button/breadcrumb nav keeping every screen mounted-but-hidden, a map
  // built while its container is display:none needs to be told to
  // remeasure once it's actually visible.
  export let visible = true;

  let mapContainer;
  let map;
  $: if (map && visible) map.resize();

  function lightenBasemap(map) {
    const textLayers = [
      'highway_name_other',
      'highway_name_motorway',
      'place_other',
      'place_suburb',
      'place_village',
      'place_town',
      'place_city',
      'place_city_large',
      'place_state',
      'place_country_other',
      'place_country_minor',
      'place_country_major',
    ];
    for (const id of textLayers) {
      if (map.getLayer(id)) map.setPaintProperty(id, 'text-color', '#e8e8e8');
    }

    const roadLayers = {
      highway_minor: '#3a3a3a',
      highway_major_subtle: '#4a4a4a',
      highway_major_inner: 'hsl(0,0%,30%)',
      highway_motorway_subtle: '#3a3a3a',
      highway_path: 'rgb(60,60,62)',
    };
    for (const [id, color] of Object.entries(roadLayers)) {
      if (map.getLayer(id)) map.setPaintProperty(id, 'line-color', color);
    }
  }

  onMount(() => {
    (async () => {
      const maplibregl = (await import('maplibre-gl')).default;

      map = new maplibregl.Map({
      container: mapContainer,
      style: 'https://tiles.openfreemap.org/styles/dark',
      center: [-71.06, 42.33],
      zoom: 11.5,
      interactive: false, // background only — no pan/zoom/click on this screen
    });

      map.on('load', async () => {
        lightenBasemap(map);

        try {
          const res = await fetch(CRASH_DATA_URL);
          if (!res.ok) throw new Error('no data yet');
          const geojson = await res.json();

          map.addSource('crashes', { type: 'geojson', data: geojson });
          map.addLayer({
            id: 'hero-heatmap',
            type: 'heatmap',
            source: 'crashes',
            filter: ['in', ['get', 'provenance'], ['literal', ['both', 'vz_only', 'massdot_only']]],
            paint: {
            // Weight: checked first whether a real field should drive this
            // (e.g. severity) instead of a flat 1-per-point. Rejected —
            // severity is only populated for 453 of 1,742 records (the
            // ones with a MassDOT-side match), so weighting the whole
            // heatmap by a 74%-null field would misrepresent density as
            // something closer to "severity," and the project's own
            // guardrails already rule out implying danger/severity from
            // raw crash counts. Flat weight = plain reported-crash density.
            'heatmap-weight': 1,
            'heatmap-intensity': 1.4,
            'heatmap-radius': 22,
            'heatmap-opacity': 0.85,
            // Single-hue sequential ramp (2026-08-10): blue/pink removed —
            // those colors are reserved elsewhere in the app for
            // match-provenance categories (911-only, both-sources), and
            // reusing them here as density colors created a false visual
            // association before the reader has learned what those colors
            // mean. This heatmap reads purely as "where crashes cluster,"
            // orange intensity only, anchored on the same #f2ad50 already
            // used as the peak color in the retired ramp — no new hue
            // introduced, just the blue/pink midtones replaced with
            // increasing depth of the same orange.
            'heatmap-color': [
              'interpolate',
              ['linear'],
              ['heatmap-density'],
              0, 'rgba(242,173,80,0)',
              0.2, 'rgba(242,173,80,0.35)',
              0.45, 'rgba(240,150,50,0.6)',
              0.7, 'rgba(235,110,20,0.85)',
              1, '#e6550d',
            ],
          },
          });
        } catch (e) {
          console.warn('Hero map crash data not loaded yet:', e.message);
        }
      });

      })();
    });

  onDestroy(() => {
    if (map) map.remove();
  });
</script>

<div bind:this={mapContainer} class="hero-map"></div>

<style>
  .hero-map {
    width: 100%;
    height: 100%;
  }
</style>
