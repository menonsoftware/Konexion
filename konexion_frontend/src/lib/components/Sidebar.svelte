<script>
	import { maxTokens } from '$lib/stores.js';
	import MaxTokensSelector from './MaxTokensSelector.svelte';
	import ClearChatButton from './ClearChatButton.svelte';
	import RefreshModelsButton from './RefreshModelsButton.svelte';

	let { isOpen = false, onToggle } = $props();

	function handleToggle() {
		if (onToggle) {
			onToggle();
		}
	}

	function handleClickOutside(event) {
		if (
			isOpen &&
			!event.target.closest('.sidebar-content') &&
			!event.target.closest('.sidebar-toggle')
		) {
			if (onToggle) {
				onToggle();
			}
		}
	}
</script>

<svelte:window on:click={handleClickOutside} />

<!-- Sidebar Toggle Button -->
<button
	type="button"
	onclick={handleToggle}
	class="sidebar-toggle fixed top-20 right-4 z-30 rounded-lg border border-gray-300 bg-white p-2 shadow-lg transition-all duration-200 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:hover:bg-gray-700"
	title={isOpen ? 'Close sidebar' : 'Open settings'}
	aria-label={isOpen ? 'Close sidebar' : 'Open settings'}
>
	<svg
		class="h-5 w-5 text-gray-600 transition-transform duration-200 dark:text-gray-400 {isOpen
			? 'rotate-180'
			: ''}"
		fill="none"
		stroke="currentColor"
		viewBox="0 0 24 24"
	>
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			stroke-width="2"
			d="M10.5 6L9 7.5 6 10.5m0 0l3 3L10.5 15M6 10.5h14.25"
		/>
	</svg>
</button>

<!-- Sidebar Overlay -->
{#if isOpen}
	<div class="bg-opacity-50 fixed inset-0 z-20 bg-black transition-opacity duration-200"></div>
{/if}

<!-- Sidebar Content -->
<div
	class="sidebar-content fixed top-0 right-0 z-25 h-full w-80 transform border-l border-gray-300 bg-white shadow-2xl transition-transform duration-300 ease-in-out dark:border-gray-600 dark:bg-gray-800 {isOpen
		? 'translate-x-0'
		: 'translate-x-full'}"
>
	<div class="flex h-full flex-col">
		<!-- Sidebar Header -->
		<div
			class="flex items-center justify-between border-b border-gray-200 p-4 dark:border-gray-700"
		>
			<h3 class="text-lg font-semibold text-gray-900 dark:text-white">Settings</h3>
			<button
				type="button"
				onclick={handleToggle}
				class="rounded-md p-1 transition-colors hover:bg-gray-100 dark:hover:bg-gray-700"
				title="Close sidebar"
				aria-label="Close sidebar"
			>
				<svg
					class="h-5 w-5 text-gray-500 dark:text-gray-400"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M6 18L18 6M6 6l12 12"
					/>
				</svg>
			</button>
		</div>

		<!-- Sidebar Content -->
		<div class="flex-1 overflow-y-auto p-4">
			<div class="space-y-6">
				<!-- Chat Management Section -->
				<div>
					<h4 class="mb-3 text-sm font-medium text-gray-900 dark:text-white">Chat Management</h4>
					<div class="space-y-3">
						<ClearChatButton />
					</div>
				</div>

				<!-- Model Management Section -->
				<div>
					<h4 class="mb-3 text-sm font-medium text-gray-900 dark:text-white">Model Management</h4>
					<div class="space-y-3">
						<div class="rounded-lg bg-gray-50 p-3 dark:bg-gray-700">
							<div class="mb-2 flex items-start justify-between">
								<div>
									<div class="text-sm font-medium text-gray-700 dark:text-gray-300">
										Refresh Models
									</div>
									<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
										Update the model list from AI providers
									</div>
								</div>
							</div>
							<RefreshModelsButton size="sm" variant="secondary" showText={true} />
						</div>
					</div>
				</div>

				<!-- AI Settings Section -->
				<div>
					<h4 class="mb-3 text-sm font-medium text-gray-900 dark:text-white">AI Configuration</h4>
					<div class="space-y-3">
						<!-- Max Tokens Setting -->
						<div class="rounded-lg bg-gray-50 p-3 dark:bg-gray-700">
							<div class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
								Max Tokens
							</div>
							<div class="mb-2 text-xs text-gray-500 dark:text-gray-400">
								Maximum number of tokens to generate in the response.
							</div>
							<MaxTokensSelector showLabel={false} />
						</div>

						<!-- Current Token Value Display -->
						<div class="text-xs text-gray-500 dark:text-gray-400">
							Current: <span class="font-mono text-blue-600 dark:text-blue-400"
								>{$maxTokens.toLocaleString()}</span
							> tokens
						</div>
					</div>
				</div>

				<!-- Future Settings Placeholder -->
				<div>
					<h4 class="mb-3 text-sm font-medium text-gray-900 dark:text-white">Advanced</h4>
					<div class="text-xs text-gray-500 dark:text-gray-400">
						Additional settings coming soon...
					</div>
				</div>
			</div>
		</div>

		<!-- Sidebar Footer -->
		<div class="border-t border-gray-200 p-4 dark:border-gray-700">
			<div class="text-center text-xs text-gray-500 dark:text-gray-400">
				Use <kbd class="rounded bg-gray-200 px-1 py-0.5 text-xs dark:bg-gray-600">Ctrl+,</kbd> to toggle
				this panel
			</div>
		</div>
	</div>
</div>

<style>
	kbd {
		font-family:
			ui-monospace, SFMono-Regular, 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace;
	}
</style>
