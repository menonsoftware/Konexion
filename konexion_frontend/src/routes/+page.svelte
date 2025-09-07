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
  import { wsService } from '$lib/websocket.js';
  import { fetchAvailableModels } from '$lib/api.js';
  import { availableModels, selectedModel, isConnected, isDarkMode } from '$lib/stores.js';

  let isInitialized = false;
  let initError = null;
  let showShortcuts = false;

  async function initialize() {
    try {
      initError = null;
      isInitialized = false;
      
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
    
    // Ctrl/Cmd + Shift + D to toggle dark mode
    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'D') {
      event.preventDefault();
      isDarkMode.toggle();
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

<div class="h-screen flex flex-col bg-gray-100 dark:bg-gray-900">
  <Header />
  
  <main class="flex-1 flex flex-col overflow-hidden bg-white dark:bg-gray-800">
    {#if initError}
      <ErrorMessage 
        title="Initialization Failed" 
        message={initError} 
        onRetry={initialize}
      />
    {:else if isInitialized}
      <ChatWindow />
      <ChatInput />
    {:else}
      <LoadingSpinner message="Initializing WebKonexion..." />
    {/if}
  </main>

  <ConnectionStatus />
</div>

<KeyboardShortcuts bind:show={showShortcuts} />
