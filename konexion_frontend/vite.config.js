import devtoolsJson from 'vite-plugin-devtools-json';
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	// Load env file based on `mode` in the current working directory.
	const env = loadEnv(mode, process.cwd(), '');
	const wsHost = env.VITE_WS_HOST?.split(':')[0]?.trim();
	const extraAllowedHosts = (env.DEV_SERVER_ALLOWED_HOSTS?.split(',') ?? [])
		.map((h) => h.trim())
		.filter(Boolean);
	const allowedHosts = [
		...new Set(['localhost', '127.0.0.1', ...extraAllowedHosts, ...(wsHost ? [wsHost] : [])])
	];

	const proxyTarget = env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000';

	return {
		plugins: [tailwindcss(), sveltekit(), devtoolsJson()],
		server: {
			allowedHosts,
			proxy: {
				[env.VITE_API_PROXY_PATH || '/api']: {
					target: proxyTarget,
					changeOrigin: true,
					secure: false
				},
				// Same-origin wss in dev (e.g. HTTPS reverse proxy → Vite): browser → Vite → plain ws on backend.
				'/ws': {
					target: proxyTarget,
					changeOrigin: true,
					secure: false,
					ws: true
				}
			},
			cors: false
		}
	};
});
