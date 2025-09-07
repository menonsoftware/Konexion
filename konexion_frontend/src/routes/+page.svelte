<script>
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import Header from '$lib/components/Header.svelte';
	import ChatWindow from '$lib/components/ChatWindow.svelte';
	import ChatInput from '$lib/components/ChatInput.svelte';
	import ConnectionStatus from '$lib/components/ConnectionStatus.svelte';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import ErrorMessage from '$lib/components/ErrorMessage.svelte';
	import KeyboardShortcuts from '$lib/components/KeyboardShortcuts.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Modal from '$lib/components/Modal.svelte';
	import { wsService } from '$lib/websocket.js';
	import { fetchAvailableModels } from '$lib/api.js';
	import {
		availableModels,
		selectedModel,
		isConnected,
		isDarkMode,
		maxTokens,
		globalModal,
		modelsRefreshState
	} from '$lib/stores.js';

	let isInitialized = false;
	let initError = null;
	let showShortcuts = false;
	let showSidebar = false;

	async function initialize() {
		try {
			initError = null;
			isInitialized = false;

			// Initialize stores
			isDarkMode.init();
			maxTokens.init();

			// Fetch available models
			const models = await fetchAvailableModels();
			availableModels.set(models);

			// Set default model if available
			if (models.length > 0) {
				selectedModel.set(models[0].model_id);
			}

			// Initialize WebSocket connection
			wsService.connect();

			isInitialized = true;
		} catch (error) {
			console.error('Failed to initialize app:', error);
			initError = error.message;
		}
	}

	// Handle keyboard shortcuts
	function handleKeydown(event) {
		if (!browser) return; // Only run on client side

		// Ctrl/Cmd + Shift + K to focus message input
		if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'K') {
			event.preventDefault();
			const messageInput = document.getElementById('message-input');
			if (messageInput) messageInput.focus();
		}

		// Ctrl/Cmd + Shift + I to trigger image attachment
		if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'I') {
			event.preventDefault();
			const imageInput = document.querySelector('input[type="file"][accept="image/*"]');
			if (imageInput) imageInput.click();
		}

		// Ctrl/Cmd + Shift + D to toggle dark mode
		if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'D') {
			event.preventDefault();
			isDarkMode.toggle();
		}

		// Ctrl/Cmd + Shift + Delete to clear chat
		if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'Delete') {
			event.preventDefault();
			// Trigger clear chat by dispatching a custom event
			window.dispatchEvent(new CustomEvent('clearChatShortcut'));
		}

		// Ctrl/Cmd + , to toggle settings sidebar
		if ((event.ctrlKey || event.metaKey) && event.key === ',') {
			event.preventDefault();
			showSidebar = !showSidebar;
		}

		// ? to show keyboard shortcuts
		if (event.key === '?' && !event.ctrlKey && !event.metaKey && !event.altKey) {
			const activeElement = document.activeElement;
			// Only show help if not typing in an input
			if (activeElement?.tagName !== 'INPUT' && activeElement?.tagName !== 'TEXTAREA') {
				event.preventDefault();
				showShortcuts = true;
			}
		}
	}

	onMount(() => {
		initialize();
		if (browser) {
			document.addEventListener('keydown', handleKeydown);
		}
	});

	onDestroy(() => {
		if (wsService) {
			wsService.disconnect();
		}
		if (browser) {
			document.removeEventListener('keydown', handleKeydown);
		}
	});
</script>

<svelte:head>
	<title>WebKonexion - AI Chat Assistant</title>
</svelte:head>

<div class="flex h-screen flex-col bg-gray-100 dark:bg-gray-900">
	<Header />

	<main class="flex flex-1 flex-col overflow-hidden bg-white dark:bg-gray-800">
		{#if initError}
			<ErrorMessage title="Initialization Failed" message={initError} onRetry={initialize} />
		{:else if isInitialized}
			<ChatWindow />
			<ChatInput />
		{:else}
			<LoadingSpinner message="Initializing WebKonexion..." />
		{/if}
	</main>

	<ConnectionStatus />

	<!-- Settings Sidebar -->
	<Sidebar isOpen={showSidebar} onToggle={() => (showSidebar = !showSidebar)} />
</div>

<KeyboardShortcuts bind:show={showShortcuts} />

<!-- Global Modal -->
<Modal
	show={$globalModal.show}
	title={$globalModal.title}
	description={$globalModal.description}
	content={$globalModal.content}
	confirmText={$globalModal.confirmText}
	cancelText={$globalModal.cancelText}
	confirmClass={$globalModal.confirmClass}
	cancelClass={$globalModal.cancelClass}
	icon={$globalModal.icon}
	onConfirm={$globalModal.onConfirm}
	onCancel={$globalModal.onCancel}
/>
