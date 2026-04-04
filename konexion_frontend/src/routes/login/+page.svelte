<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { availableProviders, checkAuth, loadProviders, login } from '$lib/auth.js';
	import { isDarkMode } from '$lib/stores.js';
	import konexionLogo from '$lib/assets/konexion.png';

	let loading = true;
	let signingIn = null; // provider id currently being used

	const PROVIDER_ICONS = {
		google: `<svg class="h-5 w-5" viewBox="0 0 24 24" aria-hidden="true">
			<path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
			<path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
			<path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
			<path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
		</svg>`,
		microsoft: `<svg class="h-5 w-5" viewBox="0 0 23 23" aria-hidden="true">
			<path fill="#f25022" d="M1 1h10v10H1z"/>
			<path fill="#00a4ef" d="M12 1h10v10H12z"/>
			<path fill="#7fba00" d="M1 12h10v10H1z"/>
			<path fill="#ffb900" d="M12 12h10v10H12z"/>
		</svg>`
	};

	onMount(async () => {
		isDarkMode.init();
		const authed = await checkAuth();
		if (authed) {
			goto('/');
			return;
		}
		await loadProviders();
		loading = false;
	});

	async function handleLogin(providerId) {
		signingIn = providerId;
		login(providerId);
	}
</script>

<svelte:head>
	<title>Sign in — WebKonexion</title>
</svelte:head>

<div
	class="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-4 dark:bg-gray-900"
>
	<div class="w-full max-w-sm">
		<!-- Logo -->
		<div class="mb-8 flex flex-col items-center space-y-3">
			<div class="flex h-14 w-14 items-center justify-center overflow-hidden rounded-2xl shadow-md">
				<img src={konexionLogo} alt="Konexion Logo" class="h-full w-full object-contain" />
			</div>
			<div class="text-center">
				<h1 class="text-2xl font-bold text-gray-900 dark:text-white">WebKonexion</h1>
				<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
					Sign in to your account to continue
				</p>
			</div>
		</div>

		<!-- Card -->
		<div
			class="rounded-2xl border border-gray-200 bg-white px-8 py-8 shadow-sm dark:border-gray-700 dark:bg-gray-800"
		>
			{#if loading}
				<div class="flex justify-center py-6">
					<svg class="h-6 w-6 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
						></circle>
						<path
							class="opacity-75"
							fill="currentColor"
							d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
						></path>
					</svg>
				</div>
			{:else if $availableProviders.length === 0}
				<p class="text-center text-sm text-gray-500 dark:text-gray-400">
					No sign-in providers are configured. Please contact your administrator.
				</p>
			{:else}
				<p class="mb-5 text-center text-sm font-medium text-gray-600 dark:text-gray-300">
					Choose a sign-in method
				</p>
				<div class="space-y-3">
					{#each $availableProviders as provider (provider.id)}
						<button
							onclick={() => handleLogin(provider.id)}
							disabled={signingIn !== null}
							class="relative flex w-full items-center justify-center gap-3 rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed disabled:opacity-60 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
						>
							{#if signingIn === provider.id}
								<svg class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
									<circle
										class="opacity-25"
										cx="12"
										cy="12"
										r="10"
										stroke="currentColor"
										stroke-width="4"
									></circle>
									<path
										class="opacity-75"
										fill="currentColor"
										d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
									></path>
								</svg>
							{:else}
								<!-- eslint-disable-next-line svelte/no-at-html-tags -->
								{@html PROVIDER_ICONS[provider.icon_hint] ?? ''}
							{/if}
							<span>Continue with {provider.name}</span>
						</button>
					{/each}
				</div>
			{/if}
		</div>

		<p class="mt-6 text-center text-xs text-gray-400 dark:text-gray-500">
			By signing in you agree to our terms of service and privacy policy.
		</p>
	</div>
</div>
