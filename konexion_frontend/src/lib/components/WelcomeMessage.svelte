<script>
	import { onMount } from 'svelte';
	import konexionLogo from '$lib/assets/konexion.png';

	let currentTime = '';
	let weatherInfo = '';

	onMount(() => {
		// Update time
		const updateTime = () => {
			const now = new Date();
			currentTime = now.toLocaleString('en-US', {
				weekday: 'long',
				year: 'numeric',
				month: 'long',
				day: 'numeric',
				hour: '2-digit',
				minute: '2-digit'
			});
		};

		updateTime();
		const timeInterval = setInterval(updateTime, 60000); // Update every minute

		// Simple weather info (you could integrate with a weather API)
		weatherInfo = 'Welcome to your AI assistant';

		return () => {
			clearInterval(timeInterval);
		};
	});
</script>

<div class="fade-in py-8 text-center">
	<div class="mb-6">
		<div
			class="mx-auto mb-4 flex h-16 w-16 items-center justify-center overflow-hidden rounded-2xl bg-white p-2 dark:bg-gray-100"
		>
			<img src={konexionLogo} alt="Konexion Logo" class="h-full w-full object-contain" />
		</div>
		<h2 class="mb-2 text-2xl font-bold text-gray-900 dark:text-white">WebKonexion</h2>
		<p class="mb-4 text-lg text-gray-700 dark:text-gray-300">Converse Smarter. Solve Faster.</p>
	</div>

	<div
		class="mx-auto max-w-md rounded-xl border border-gray-300 bg-gray-50 p-6 shadow-sm dark:border-gray-600 dark:bg-gray-700"
	>
		<div class="mb-2 text-sm text-gray-600 dark:text-gray-400">
			{currentTime}
		</div>
		<div class="text-sm font-medium text-blue-600 dark:text-blue-400">
			{weatherInfo}
		</div>
	</div>

	<div class="mt-6 text-sm text-gray-600 dark:text-gray-400">Send a message to get started</div>
</div>
