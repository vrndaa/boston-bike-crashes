<script>
  import { onMount, onDestroy, afterUpdate } from 'svelte';
  import maplibregl from 'maplibre-gl';

  export let selectedRange = null;
  export let activeProvenance = null; // Set of provenance keys to show; null/undefined = show all
  export let showCrashes = true; // "The Gap" tab layer visibility
  export let showConcerns = false; // "What People Are Afraid Of" tab layer visibility
  // Button/breadcrumb navigation now keeps every screen mounted at once
  // (just hidden via CSS) instead of destroying/recreating the map on
  // every nav click — cheaper, and keeps pan/zoom + brush state intact.
  // But a map created while its container is display:none gets a 0×0
  // canvas and never fixes itself on its own — this prop tells it when
  // it's actually back on screen so it can ask MapLibre to remeasure.
  export let visible = true;
  // Optional corridor callouts for the fear map only — [{lat, lon, title,
  // count, reason}]. Left empty on the Explorer screen's CrashMap instance.
  export let concernCallouts = [];

  let mapContainer;
  let map;
  let loaded = false;
  let concernsLoaded = false;

  $: if (map && visible) map.resize();

  const CRASH_DATA_URL = '/data/boston_bike_crashes_enriched.geojson';
  const CONCERNS_DATA_URL = '/data/safety_concerns.geojson';
  // pre_massdot excluded from "The Gap" view entirely — not a toggleable
  // category, just never rendered. See the always-applied provenance
  // clause in the crash-points filter below.
  const ALL_PROVENANCE = ['both', 'vz_only', 'massdot_only'];

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

  // Plain-language provenance for the click-to-inspect card — matches the
  // legend wording in App.svelte.
  const PROVENANCE_LABELS = {
    both: 'Confirmed by both sources',
    vz_only: '911 dispatch only',
    massdot_only: 'Police report only',
  };

  function buildCrashPopupHtml(props) {
    const streetLine =
      props.street || (props.location_type === 'Intersection' ? 'Intersection (cross streets not recorded)' : 'Location not specified');
    const date = props.timestamp_ms
      ? new Date(props.timestamp_ms).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
      : 'Date unknown';
    const provenanceLabel = PROVENANCE_LABELS[props.provenance] || props.provenance;

    return `
      <div class="crash-popup-street">${escapeHtml(streetLine)}</div>
      <div class="crash-popup-date">${escapeHtml(date)}</div>
      <div class="crash-popup-provenance">${escapeHtml(provenanceLabel)}</div>
      ${props.severity ? `<div class="crash-popup-severity">Severity: ${escapeHtml(props.severity)}</div>` : ''}
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
          layout: {
            visibility: showCrashes ? 'visible' : 'none',
          },
          paint: {
            // Provenance paint spec (2026-07-28): three crash states from
            // the VZ/MassDOT match — see match_crashes.py for how
            // provenance is assigned. pre_massdot is excluded from this
            // view entirely (see the filter below), so it has no branch
            // here. All three render as solid filled circles, no stroke —
            // distinguished by color alone. Colors match Screen 2's
            // stat-number palette for consistency across the piece.
            'circle-radius': ['match', ['get', 'provenance'], 'both', 3, 'vz_only', 2, 'massdot_only', 2, 2],
            'circle-color': [
              'match',
              ['get', 'provenance'],
              'both', '#e28aab',
              'vz_only', '#7fb2e5',
              'massdot_only', '#f2d06b',
              '#f2d06b', // fallback
            ],
          },
        });

        // Click-to-inspect: a styled detail card (not a browser tooltip),
        // dismissed by its own close button or by clicking elsewhere —
        // both closeButton and closeOnClick are on by default.
        map.on('click', 'crash-points', (e) => {
          const feature = e.features[0];
          new maplibregl.Popup({
            className: 'crash-popup',
            offset: 10,
          })
            .setLngLat(feature.geometry.coordinates)
            .setHTML(buildCrashPopupHtml(feature.properties))
            .addTo(map);
        });
        map.on('mouseenter', 'crash-points', () => {
          map.getCanvas().style.cursor = 'pointer';
        });
        map.on('mouseleave', 'crash-points', () => {
          map.getCanvas().style.cursor = '';
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

        // Corridor callouts (Longwood / Mass Ave): a soft geographic ring
        // stays on the map (real layer, auto-tracks pan/zoom) marking
        // roughly where the corridor is, but the text box itself is no
        // longer geo-anchored — it used to sit right on top of the dots
        // it was describing, so it's now a fixed corner overlay instead
        // (rendered in the template below, positioned via c.corner).
        if (concernCallouts.length) {
          map.addSource('concern-callouts', {
            type: 'geojson',
            data: {
              type: 'FeatureCollection',
              features: concernCallouts.map((c) => ({
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [c.lon, c.lat] },
                properties: {},
              })),
            },
          });
          map.addLayer(
            {
              id: 'concern-callout-rings',
              type: 'circle',
              source: 'concern-callouts',
              paint: {
                'circle-radius': 42,
                'circle-color': 'transparent',
                'circle-stroke-color': '#f2d06b',
                'circle-stroke-width': 2,
                'circle-stroke-opacity': 0.55,
              },
            },
            'concern-points'
          );
        }
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
  // a provenance legend toggle can both be active at once. The provenance
  // clause is always applied (not just when a category is toggled off) so
  // pre_massdot rows are never rendered on this tab.
  afterUpdate(() => {
    if (!loaded || !map.getLayer('crash-points')) return;

    const clauses = ['all'];

    if (selectedRange) {
      clauses.push(['>=', ['get', 'timestamp_ms'], selectedRange.start.getTime()]);
      clauses.push(['<=', ['get', 'timestamp_ms'], selectedRange.end.getTime()]);
    }

    const activeList = activeProvenance ? [...activeProvenance] : ALL_PROVENANCE;
    clauses.push(['in', ['get', 'provenance'], ['literal', activeList]]);

    map.setFilter('crash-points', clauses);
  });

  // Toggle layer visibility per active tab — independent of the date/
  // provenance filter above, and of each other, so switching tabs never
  // touches selectedRange or activeProvenance.
  afterUpdate(() => {
    if (loaded && map.getLayer('crash-points')) {
      map.setLayoutProperty('crash-points', 'visibility', showCrashes ? 'visible' : 'none');
    }
    if (concernsLoaded && map.getLayer('concern-points')) {
      map.setLayoutProperty('concern-points', 'visibility', showConcerns ? 'visible' : 'none');
    }
  });
</script>

<div class="map-wrap">
  <div bind:this={mapContainer} class="map"></div>
  {#each concernCallouts as c}
    <div class="concern-callout-box corner-{c.corner}">
      <div class="concern-callout-title">{c.title}</div>
      <div class="concern-callout-count">{c.count} of 176 bike concerns name this corridor</div>
      <div class="concern-callout-reason">{c.reason}</div>
    </div>
  {/each}
</div>

<style>
  .map-wrap {
    position: relative;
    width: 100%;
    height: 100%;
  }
  .map {
    width: 100%;
    height: 100%;
  }

  :global(.crash-popup .maplibregl-popup-content) {
    background: #14090f;
    color: #f2f2f2;
    border: 1px solid #ff4fa2;
    border-radius: 6px;
    padding: 0.6rem 0.75rem;
    font-family: ui-monospace, 'SFMono-Regular', 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
    font-size: 0.78rem;
    max-width: 240px;
    box-shadow: none;
  }
  :global(.crash-popup .maplibregl-popup-tip) {
    display: none;
  }
  :global(.crash-popup .maplibregl-popup-close-button) {
    color: #888;
    font-size: 1.1rem;
  }
  :global(.crash-popup .maplibregl-popup-close-button:hover) {
    color: #fff;
    background: none;
  }
  :global(.crash-popup-street) {
    font-weight: 600;
    color: #ff4fa2;
    margin-bottom: 0.3rem;
    padding-right: 0.75rem;
  }
  :global(.crash-popup-date) {
    color: #ccc;
    margin-bottom: 0.15rem;
  }
  :global(.crash-popup-provenance) {
    color: #aaa;
    margin-bottom: 0.15rem;
  }
  :global(.crash-popup-severity) {
    color: #ff9e9e;
    margin-top: 0.25rem;
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

  /* Fixed to a screen corner (not a map coordinate) so they never sit on
     top of the concern dots they're describing. */
  .concern-callout-box {
    position: absolute;
    top: 1rem;
    z-index: 2;
    background: rgba(10, 10, 10, 0.9);
    border: 1px solid #f2d06b;
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    font-family: ui-monospace, 'SFMono-Regular', 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
    max-width: 220px;
    pointer-events: none;
  }
  .corner-top-left {
    left: 1rem;
  }
  .corner-top-right {
    right: 1rem;
  }
  .concern-callout-title {
    color: #f2d06b;
    font-weight: 600;
    font-size: 0.78rem;
    margin-bottom: 0.2rem;
  }
  .concern-callout-count {
    color: #f2f2f2;
    font-size: 0.72rem;
    margin-bottom: 0.25rem;
  }
  .concern-callout-reason {
    color: #aaa;
    font-size: 0.68rem;
    line-height: 1.35;
  }
</style>
