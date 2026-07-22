<script>
  import { onMount, onDestroy, afterUpdate } from 'svelte';
  import maplibregl from 'maplibre-gl';

  export let selectedRange = null;

  let mapContainer;
  let map;
  let loaded = false;

  const CRASH_DATA_URL = '/data/boston_bike_crashes.geojson';

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
            'circle-color': '#ff4fa2',
            'circle-opacity': 0.75,
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
