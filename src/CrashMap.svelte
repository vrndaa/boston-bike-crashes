<script>
  import { onMount, onDestroy, afterUpdate } from 'svelte';
  import maplibregl from 'maplibre-gl';

  export let selectedRange = null;

  let mapContainer;
  let map;
  let loaded = false;

  // TODO (Phase 1, step 1): replace with the real path once
  // scripts/fetch_crash_data.py has produced data/boston_bike_crashes.geojson
  // and it's been copied/symlinked into public/data/.
  const CRASH_DATA_URL = '/data/boston_bike_crashes.geojson';

  onMount(() => {
    map = new maplibregl.Map({
      container: mapContainer,
      // Real labeled basemap, per CLAUDE.md — street names matter to this
      // story. Swap for a specific open style (OpenFreeMap/Protomaps) once
      // decided; using MapLibre's demo style as a placeholder for now.
      style: 'https://demotiles.maplibre.org/style.json',
      center: [-71.06, 42.33],
      zoom: 11,
    });

    map.on('load', async () => {
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
            'circle-radius': 4,
            'circle-color': '#9a3b3b',
            'circle-opacity': 0.7,
          },
        });
        loaded = true;
      } catch (e) {
        // Expected until the data pipeline has run — not an error to chase
        // down, just means CRASH_DATA_URL doesn't exist yet.
        console.warn('Crash data not loaded yet:', e.message);
      }
    });
  });

  onDestroy(() => {
    if (map) map.remove();
  });

  // Re-apply a filter whenever selectedRange changes, once the layer exists.
  afterUpdate(() => {
    if (!loaded || !map.getLayer('crash-points')) return;

    if (!selectedRange) {
      map.setFilter('crash-points', null);
      return;
    }

    const startMs = selectedRange.start.getTime();
    const endMs = selectedRange.end.getTime();
    map.setFilter('crash-points', [
      'all',
      ['>=', ['get', 'timestamp_ms'], startMs],
      ['<=', ['get', 'timestamp_ms'], endMs],
    ]);
  });
</script>

<div bind:this={mapContainer} class="map"></div>

<style>
  .map {
    width: 100%;
    height: 100%;
  }
</style>
