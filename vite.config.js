import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// GitHub Pages serves this as a project site at /boston-bike-crashes/, not
// the domain root — base must match so built asset/data URLs resolve.
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/boston-bike-crashes/' : '/',
  plugins: [svelte()],
}));
