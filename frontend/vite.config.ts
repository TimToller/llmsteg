import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [svelte()],
	server: {
		proxy: {
			"/encode": "http://backend:8000",
			"/decode": "http://backend:8000",
		},
	},
});
