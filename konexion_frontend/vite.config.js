import devtoolsJson from 'vite-plugin-devtools-json';
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	// Load env file based on `mode` in the current working directory.
	const env = loadEnv(mode, process.cwd(), '');
	const wsHost = env.VITE_WS_HOST?.split(':')[0]?.trim();
	const allowedHosts = ['localhost', '127.0.0.1', ...(wsHost ? [wsHost] : [])];

	return {
		plugins: [tailwindcss(), sveltekit(), devtoolsJson()],
		server: {
			allowedHosts,
			proxy: {
				[env.VITE_API_PROXY_PATH || '/api']: {
					target: env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000',
					changeOrigin: true,
					secure: false
				}
			},
			cors: false
		}
	};
});
