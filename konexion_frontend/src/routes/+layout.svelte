<script>
	import '../app.css';
	import favicon from '$lib/assets/konexion.png';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { isDarkMode } from '$lib/stores.js';
	import { checkAuth } from '$lib/auth.js';

	let { children } = $props();

	// Public routes that do not require authentication
	const PUBLIC_ROUTES = ['/login'];

	onMount(async () => {
		isDarkMode.init();
		const currentPath = $page.url.pathname;
		if (PUBLIC_ROUTES.includes(currentPath)) return;

		const authed = await checkAuth();
		if (!authed) {
			goto('/login');
		}
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="icon" type="image/svg+xml" href={favicon} />
	<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
	<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
	<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
	<title>WebKonexion - AI Chat Assistant</title>
	<meta name="description" content="Professional AI chat interface powered by Groq API" />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
</svelte:head>

{@render children?.()}
