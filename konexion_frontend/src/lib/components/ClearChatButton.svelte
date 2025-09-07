<script>
	import { messages, globalModal } from '$lib/stores.js';
	import { onMount } from 'svelte';

	// Check if there are any messages
	$: hasMessages = $messages.length > 0;

	function handleClearClick() {
		if (!hasMessages) return; // Don't show dialog if no messages

		// Configure and show the global modal
		globalModal.show({
			title: 'Clear Chat History',
			description: 'This action cannot be undone',
			content:
				'Are you sure you want to clear all chat messages? This will permanently delete your entire conversation history.',
			confirmText: 'Clear Chat',
			cancelText: 'Cancel',
			confirmClass:
				'px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 dark:bg-red-600 dark:hover:bg-red-700 border border-red-600 dark:border-red-600 rounded-lg transition-colors focus:ring-2 focus:ring-red-500 focus:border-red-500',
			icon: {
				svg: '<svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>',
				bgClass: 'bg-red-100 dark:bg-red-900/30'
			},
			onConfirm: () => {
				messages.clear();
				globalModal.hide();
			},
			onCancel: () => {
				globalModal.hide();
			}
		});
	}

	// Listen for keyboard shortcut
	function handleClearChatShortcut() {
		handleClearClick();
	}

	onMount(() => {
		window.addEventListener('clearChatShortcut', handleClearChatShortcut);
		return () => {
			window.removeEventListener('clearChatShortcut', handleClearChatShortcut);
		};
	});
</script>

<div class="relative">
	<!-- Clear Chat Button -->
	<button
		type="button"
		on:click={handleClearClick}
		disabled={!hasMessages}
		class="flex w-full items-center justify-center space-x-2 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-red-600 transition-colors duration-200 hover:border-red-300 hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-red-50 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400 dark:hover:border-red-700 dark:hover:bg-red-900/30 dark:disabled:hover:bg-red-900/20"
		title={hasMessages ? 'Clear all chat messages (Ctrl+Shift+Del)' : 'No messages to clear'}
		aria-label="Clear chat"
	>
		<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
			/>
		</svg>
		<span class="text-sm font-medium">Clear Chat</span>
		{#if hasMessages}
			<span class="ml-1 rounded-full bg-red-200 px-2 py-0.5 text-xs dark:bg-red-800">
				{$messages.length}
			</span>
		{/if}
	</button>
</div>
