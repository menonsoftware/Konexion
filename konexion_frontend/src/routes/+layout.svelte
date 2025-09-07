<script>
	import '../app.css';
	import favicon from '$lib/assets/konexion.png';
	import { onMount } from 'svelte';
	import { isDarkMode } from '$lib/stores.js';

	let { children } = $props();

	// Initialize dark mode on mount to ensure proper synchronization
	onMount(() => {
		isDarkMode.init();
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
