<script>
	import { browser } from '$app/environment';
	import { onMount } from 'svelte';

	export let show = false;

	function close() {
		show = false;
	}

	function handleKeydown(event) {
		if (!browser || !show) return;
		if (event.key === 'Escape') {
			close();
		}
	}

	onMount(() => {
		if (browser) {
			const handleGlobalKeydown = (event) => handleKeydown(event);
			document.addEventListener('keydown', handleGlobalKeydown);
			return () => document.removeEventListener('keydown', handleGlobalKeydown);
		}
	});
</script>

{#if show}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
	<div
		class="bg-opacity-50 fixed inset-0 z-50 flex items-center justify-center bg-black p-4"
		on:click={close}
		on:keydown={(e) => e.key === 'Escape' && close()}
		role="dialog"
		aria-modal="true"
		aria-labelledby="shortcuts-title"
		tabindex="-1"
	>
		<div class="w-full max-w-md rounded-lg bg-white p-6 dark:bg-gray-800" role="document">
			<div class="mb-4 flex items-center justify-between">
				<h2 id="shortcuts-title" class="text-lg font-semibold text-gray-900 dark:text-white">
					Keyboard Shortcuts
				</h2>
				<button
					on:click={close}
					class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
					aria-label="Close shortcuts dialog"
				>
					<svg class="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
							clip-rule="evenodd"
						/>
					</svg>
				</button>
			</div>

			<div class="space-y-3">
				<div class="flex items-center justify-between">
					<span class="text-gray-700 dark:text-gray-300">Focus message input</span>
					<kbd class="rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-700">Ctrl+Shift+K</kbd>
				</div>

				<div class="flex items-center justify-between">
					<span class="text-gray-700 dark:text-gray-300">Attach image</span>
					<kbd class="rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-700">Ctrl+Shift+I</kbd>
				</div>

				<div class="flex items-center justify-between">
					<span class="text-gray-700 dark:text-gray-300">Toggle dark mode</span>
					<kbd class="rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-700">Ctrl+Shift+D</kbd>
				</div>

				<div class="flex items-center justify-between">
					<span class="text-gray-700 dark:text-gray-300">Toggle settings</span>
					<kbd class="rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-700">Ctrl+,</kbd>
				</div>

				<div class="flex items-center justify-between">
					<span class="text-gray-700 dark:text-gray-300">Clear chat</span>
					<kbd class="rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-700">Ctrl+Shift+Del</kbd>
				</div>

				<div class="flex items-center justify-between">
					<span class="text-gray-700 dark:text-gray-300">Confirm dialog action</span>
					<kbd class="rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-700">Enter</kbd>
				</div>

				<div class="flex items-center justify-between">
					<span class="text-gray-700 dark:text-gray-300">Cancel dialog</span>
					<kbd class="rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-700">Esc</kbd>
				</div>

				<div class="flex items-center justify-between">
					<span class="text-gray-700 dark:text-gray-300">Send message</span>
					<kbd class="rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-700">Enter</kbd>
				</div>

				<div class="flex items-center justify-between">
					<span class="text-gray-700 dark:text-gray-300">New line in message</span>
					<kbd class="rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-700">Shift+Enter</kbd>
				</div>

				<div class="flex items-center justify-between">
					<span class="text-gray-700 dark:text-gray-300">Navigate model dropdown</span>
					<kbd class="rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-700">↑/↓ Arrow</kbd>
				</div>

				<div class="flex items-center justify-between">
					<span class="text-gray-700 dark:text-gray-300">Show this help</span>
					<kbd class="rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-700">?</kbd>
				</div>
			</div>
		</div>
	</div>
{/if}
