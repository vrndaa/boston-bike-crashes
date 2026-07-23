<script>
  import { onMount, onDestroy, afterUpdate } from 'svelte';
  import maplibregl from 'maplibre-gl';

  export let selectedRange = null;
  export let activeProvenance = null; // Set of provenance keys to show; null/undefined = show all
  export let showConcerns = false; // Layer 2 ("Fear Layer") visibility — off by default

  let mapContainer;
  let map;
  let loaded = false;
  let concernsLoaded = false;

  const CRASH_DATA_URL = '/data/boston_bike_crashes_enriched.geojson';
  const CONCERNS_DATA_URL = '/data/safety_concerns.geojson';
  const ALL_PROVENANCE = ['both', 'vz_only', 'massdot_only', 'pre_massdot'];

  // Boston's safety-concerns form codes each report into one of these
  // categories (confirmed against the bike-filtered rows in
  // data/safety_concerns.geojson — see scripts/fetch_safety_concerns.py).
  const REQUEST_LABELS = {
    bikefacility: 'Bike facility issue',
    yieldturn: 'Drivers not yielding on turn',
    doublepark: 'Double parking blocking lane',
    runlightssigns: 'Running red lights/signs',
    roadwaymaint: 'Roadway maintenance needed',
    yieldgoing: 'Drivers not yielding',
    speeding: 'Speeding',
    sidewalk: 'Sidewalk issue',
    visibility: 'Visibility issue',
    walksignal: 'Walk signal issue',
    awayfromside: 'Riding away from curb',
    notenoughtime: 'Not enough crossing time',
    toomanylanes: 'Too many lanes to cross',
    other: 'Other concern',
  };

  // Comments are free-text and user-submitted — escape before injecting
  // into popup HTML.
  function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = value == null ? '' : String(value);
    return div.innerHTML;
  }

  // Hover popup is a quick preview, not a full read — long submissions
  // (some run 500+ characters) get cut short rather than growing the
  // popup past the viewport.
  function truncate(text, max = 180) {
    if (text.length <= max) return text;
    return text.slice(0, max).trimEnd() + '…';
  }

  function buildConcernPopupHtml(props) {
    const label = REQUEST_LABELS[props.request] || props.request_other || props.request || 'Safety concern';
    const date = props.timestamp_ms ? new Date(props.timestamp_ms).toLocaleDateString() : null;

    return `
      <div class="concern-popup-title">What was reported: ${escapeHtml(label)}</div>
      ${props.comments ? `<div class="concern-popup-comment">${escapeHtml(truncate(props.comments))}</div>` : ''}
      ${date ? `<div class="concern-popup-date">${date}</div>` : ''}
    `;
  }

  // Brighten the OpenFreeMap "dark" style's road lines and text labels —
  // as-shipped they're tuned for a subtle backdrop, too dim once crash
  // points and UI chrome are layered on top. Overridden at runtime since
  // we don't control the remote style.json.
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
    map = new maplibregl.Map({
      container: mapContainer,
      // Real labeled basemap, per CLAUDE.md — street names matter to this
      // story. OpenFreeMap Dark: open, no API key/billing.
      style: 'https://tiles.openfreemap.org/styles/dark',
      center: [-71.06, 42.33],
      zoom: 11,
    });

    map.on('load', async () => {
      lightenBasemap(map);

      try {
        const res = await fetch(CRASH_DATA_URL);
        if (!res.ok) throw new Error('no data yet');
        const geojson = await res.json();

        map.addSource('crashes', { type: 'geojson', data: geojson });
        map.addLayer({
          id: 'crash-points',
          type: 'circle',
          source: 'crashes',
          paint: {
            // Provenance paint spec (2026-07-22): four crash states from the
            // VZ/MassDOT match — see match_crashes.py for how provenance is
            // assigned.
            'circle-radius': [
              'match',
              ['get', 'provenance'],
              'both', 3.5,
              'vz_only', 3.5,
              'massdot_only', 3,
              'pre_massdot', 2.5,
              3, // fallback
            ],
            'circle-color': [
              'match',
              ['get', 'provenance'],
              'both', '#ff4fa2',
              'massdot_only', '#ffffff',
              'transparent', // vz_only and pre_massdot are hollow
            ],
            'circle-stroke-color': [
              'match',
              ['get', 'provenance'],
              'vz_only', '#ff4fa2',
              'pre_massdot', '#ff4fa2',
              'transparent',
            ],
            'circle-stroke-width': [
              'match',
              ['get', 'provenance'],
              'vz_only', 1.5,
              'pre_massdot', 1,
              0,
            ],
            'circle-opacity': [
              'match',
              ['get', 'provenance'],
              'pre_massdot', 0.35,
              'massdot_only', 0.9,
              1.0,
            ],
            'circle-stroke-opacity': [
              'match',
              ['get', 'provenance'],
              'pre_massdot', 0.35,
              1.0,
            ],
          },
        });
        loaded = true;
      } catch (e) {
        // Expected until the data pipeline has run — not an error to chase
        // down, just means CRASH_DATA_URL doesn't exist yet.
        console.warn('Crash data not loaded yet:', e.message);
      }

      try {
        const res = await fetch(CONCERNS_DATA_URL);
        if (!res.ok) throw new Error('no data yet');
        const geojson = await res.json();

        map.addSource('concerns', { type: 'geojson', data: geojson });
        map.addLayer({
          id: 'concern-points',
          type: 'circle',
          source: 'concerns',
          // Bike-related citizen safety concerns only, matching the "176
          // bike-related reports" toggle label — the source geojson keeps
          // all modes so this can broaden later without re-pulling data.
          filter: ['==', ['get', 'mode'], 'bike'],
          layout: {
            visibility: showConcerns ? 'visible' : 'none',
          },
          paint: {
            'circle-radius': 4,
            'circle-color': '#ffb444',
            'circle-opacity': 0.5,
          },
        });
        concernsLoaded = true;

        // Hover popup: "what was reported" for the crash point under the
        // cursor. One popup instance, moved/rewritten on mousemove rather
        // than recreated, so it doesn't flicker between adjacent points.
        let concernPopup = null;
        map.on('mouseenter', 'concern-points', (e) => {
          map.getCanvas().style.cursor = 'pointer';
          const feature = e.features[0];
          concernPopup = new maplibregl.Popup({
            closeButton: false,
            closeOnClick: false,
            className: 'concern-popup',
            offset: 10,
          })
            .setLngLat(feature.geometry.coordinates)
            .setHTML(buildConcernPopupHtml(feature.properties))
            .addTo(map);
        });
        map.on('mousemove', 'concern-points', (e) => {
          if (!concernPopup) return;
          const feature = e.features[0];
          concernPopup.setLngLat(feature.geometry.coordinates).setHTML(buildConcernPopupHtml(feature.properties));
        });
        map.on('mouseleave', 'concern-points', () => {
          map.getCanvas().style.cursor = '';
          if (concernPopup) {
            concernPopup.remove();
            concernPopup = null;
          }
        });
      } catch (e) {
        console.warn('Safety concerns data not loaded yet:', e.message);
      }
    });
  });

  onDestroy(() => {
    if (map) map.remove();
  });

  // Re-apply a filter whenever selectedRange or activeProvenance changes,
  // once the layer exists. The two filters combine: a date-range brush and
  // a provenance legend toggle can both be active at once.
  afterUpdate(() => {
    if (!loaded || !map.getLayer('crash-points')) return;

    const clauses = ['all'];

    if (selectedRange) {
      clauses.push(['>=', ['get', 'timestamp_ms'], selectedRange.start.getTime()]);
      clauses.push(['<=', ['get', 'timestamp_ms'], selectedRange.end.getTime()]);
    }

    const activeList = activeProvenance ? [...activeProvenance] : ALL_PROVENANCE;
    if (activeList.length < ALL_PROVENANCE.length) {
      clauses.push(['in', ['get', 'provenance'], ['literal', activeList]]);
    }

    map.setFilter('crash-points', clauses.length > 1 ? clauses : null);
  });

  // Toggle Layer 2 visibility independently of the crash-points filter
  // above — showConcerns is a simple on/off, no date or provenance logic.
  afterUpdate(() => {
    if (!concernsLoaded || !map.getLayer('concern-points')) return;
    map.setLayoutProperty('concern-points', 'visibility', showConcerns ? 'visible' : 'none');
  });
</script>

<div bind:this={mapContainer} class="map"></div>

<style>
  .map {
    width: 100%;
    height: 100%;
  }

  :global(.concern-popup .maplibregl-popup-content) {
    background: #1a1408;
    color: #f2f2f2;
    border: 1px solid #ffb444;
    border-radius: 6px;
    padding: 0.6rem 0.75rem;
    font-family: ui-monospace, 'SFMono-Regular', 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
    font-size: 0.78rem;
    max-width: 240px;
    box-shadow: none;
  }
  :global(.concern-popup .maplibregl-popup-tip) {
    display: none;
  }
  :global(.concern-popup-title) {
    font-weight: 600;
    color: #ffb444;
    margin-bottom: 0.3rem;
  }
  :global(.concern-popup-comment) {
    color: #ddd;
    line-height: 1.35;
    margin-bottom: 0.3rem;
  }
  :global(.concern-popup-date) {
    color: #888;
    font-size: 0.7rem;
  }
</style>
