<script>
	import { refreshModels, fetchAvailableModels } from '$lib/api.js';
	import { availableModels, selectedModel, modelsRefreshState, globalModal } from '$lib/stores.js';

	export let size = 'md'; // 'sm', 'md', 'lg', 'header'
	export let variant = 'primary'; // 'primary', 'secondary', 'ghost'
	export let showText = true;
	export let disabled = false;

	let isRefreshing = false;

	$: isRefreshing = $modelsRefreshState.isRefreshing;

	// Size classes
	const sizeClasses = {
		sm: 'px-2 py-1 text-xs',
		md: 'px-3 py-2 text-sm',
		lg: 'px-4 py-3 text-base',
		header: 'p-2' // Matches other header buttons
	};

	// Icon size classes
	const iconSizeClasses = {
		sm: 'h-3 w-3',
		md: 'h-4 w-4',
		lg: 'h-5 w-5',
		header: 'h-5 w-5' // Matches other header button icons
	};

	// Variant classes
	const variantClasses = {
		primary: 'bg-blue-600 hover:bg-blue-700 text-white border-blue-600 hover:border-blue-700',
		secondary: 'bg-gray-600 hover:bg-gray-700 text-white border-gray-600 hover:border-gray-700',
		ghost:
			size === 'header'
				? 'bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-300'
				: 'bg-transparent hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600'
	};

	async function handleRefresh() {
		if (isRefreshing || disabled) return;

		try {
			modelsRefreshState.setRefreshing(true);

			const result = await refreshModels();

			if (result.success) {
				// Fetch updated models list
				const updatedModels = await fetchAvailableModels();
				availableModels.set(updatedModels);

				// Verify selected model still exists, otherwise select first available
				const currentSelected = $selectedModel;
				const modelExists = updatedModels.some((model) => model.model_id === currentSelected);

				if (!modelExists && updatedModels.length > 0) {
					selectedModel.set(updatedModels[0].model_id);
				}

				modelsRefreshState.setResult({
					success: true,
					message: `Successfully refreshed ${result.totalModels} models (${result.groqModels} Groq, ${result.ollamaModels} Ollama)`,
					totalModels: result.totalModels,
					groqModels: result.groqModels,
					ollamaModels: result.ollamaModels
				});

				// Show success notification
				globalModal.show({
					title: '🎉 Models Refreshed Successfully',
					content: `<div class="text-sm text-gray-600 dark:text-gray-400">
						<p class="mb-2">Model cache has been refreshed:</p>
						<ul class="list-disc pl-5 space-y-1">
							<li><strong>${result.totalModels}</strong> total models loaded</li>
							<li><strong>${result.groqModels}</strong> Groq models</li>
							<li><strong>${result.ollamaModels}</strong> Ollama models</li>
						</ul>
						<p class="mt-3 text-xs text-gray-500">
							Refreshed at ${new Date().toLocaleTimeString()}
						</p>
					</div>`,
					confirmText: 'Great!',
					cancelText: null,
					confirmClass:
						'px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 border border-green-600 rounded-lg transition-colors',
					onConfirm: () => globalModal.hide()
				});
			} else {
				modelsRefreshState.setResult({
					success: false,
					error: result.error,
					message: `Failed to refresh models: ${result.error}`
				});

				// Show error notification
				globalModal.show({
					title: '❌ Refresh Failed',
					content: `<div class="text-sm text-gray-600 dark:text-gray-400">
						<p class="mb-2">Failed to refresh model cache:</p>
						<div class="text-red-600 dark:text-red-400 font-mono bg-red-50 dark:bg-red-900/20 p-2 rounded">
							${result.error}
						</div>
						<p class="mt-2 text-xs text-gray-500">
							You can try refreshing again or check your connection to the backend.
						</p>
					</div>`,
					confirmText: 'Try Again',
					cancelText: 'Close',
					confirmClass:
						'px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 border border-blue-600 rounded-lg transition-colors',
					onConfirm: () => {
						globalModal.hide();
						setTimeout(handleRefresh, 100);
					},
					onCancel: () => globalModal.hide()
				});
			}
		} catch (error) {
			console.error('Error during model refresh:', error);

			modelsRefreshState.setResult({
				success: false,
				error: error.message,
				message: `Unexpected error: ${error.message}`
			});

			globalModal.show({
				title: '❌ Unexpected Error',
				content: `<div class="text-sm text-gray-600 dark:text-gray-400">
					<p class="mb-2">An unexpected error occurred:</p>
					<div class="text-red-600 dark:text-red-400 font-mono bg-red-50 dark:bg-red-900/20 p-2 rounded">
						${error.message}
					</div>
				</div>`,
				confirmText: 'Close',
				cancelText: null,
				onConfirm: () => globalModal.hide()
			});
		}
	}

	// Keyboard shortcut (Ctrl/Cmd + R to refresh)
	function handleKeydown(event) {
		if ((event.ctrlKey || event.metaKey) && event.key === 'r' && !isRefreshing && !disabled) {
			event.preventDefault();
			handleRefresh();
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />

<button
	class="inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50 {sizeClasses[
		size
	]} {variantClasses[variant]} {size !== 'header' ? 'border' : ''}"
	class:animate-spin={isRefreshing}
	{disabled}
	on:click={handleRefresh}
	title={isRefreshing ? 'Refreshing models...' : 'Refresh models (Ctrl/Cmd + R)'}
	aria-label={isRefreshing ? 'Refreshing models' : 'Refresh models'}
>
	<!-- Refresh Icon -->
	<svg
		class="{iconSizeClasses[size]} {showText ? 'mr-2' : ''}"
		class:animate-spin={isRefreshing}
		fill="none"
		stroke="currentColor"
		viewBox="0 0 24 24"
		aria-hidden="true"
	>
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			stroke-width="2"
			d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		/>
	</svg>

	{#if showText}
		<span class="whitespace-nowrap">
			{isRefreshing ? 'Refreshing...' : 'Refresh Models'}
		</span>
	{/if}
</button>

<style>
	/* Custom animation for better visual feedback */
	.animate-spin {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}
</style>
