<script>
  import { messages } from '$lib/stores.js';
  import { onMount } from 'svelte';
  
  let showConfirmDialog = false;
  
  // Check if there are any messages
  $: hasMessages = $messages.length > 0;
  
  function handleClearClick() {
    if (!hasMessages) return; // Don't show dialog if no messages
    showConfirmDialog = true;
  }
  
  function confirmClear() {
    messages.clear();
    showConfirmDialog = false;
  }
  
  function cancelClear() {
    showConfirmDialog = false;
  }
  
  // Close dialog on escape key
  function handleKeydown(event) {
    if (event.key === 'Escape' && showConfirmDialog) {
      cancelClear();
    }
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

<svelte:window on:keydown={handleKeydown} />

<div class="relative">
  <!-- Clear Chat Button -->
  <button
    type="button"
    on:click={handleClearClick}
    disabled={!hasMessages}
    class="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-red-50 hover:bg-red-100 dark:bg-red-900/20 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 rounded-lg transition-colors duration-200 hover:border-red-300 dark:hover:border-red-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-red-50 dark:disabled:hover:bg-red-900/20"
    title={hasMessages ? "Clear all chat messages (Ctrl+Shift+Del)" : "No messages to clear"}
    aria-label="Clear chat"
  >
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
    <span class="text-sm font-medium">Clear Chat</span>
    {#if hasMessages}
      <span class="text-xs bg-red-200 dark:bg-red-800 px-2 py-0.5 rounded-full ml-1">
        {$messages.length}
      </span>
    {/if}
  </button>

  <!-- Confirmation Dialog -->
  {#if showConfirmDialog}
    <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6 border border-gray-200 dark:border-gray-600">
        <!-- Dialog Header -->
        <div class="flex items-center space-x-3 mb-4">
          <div class="flex-shrink-0 w-10 h-10 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
            <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Clear Chat History</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">This action cannot be undone</p>
          </div>
        </div>

        <!-- Dialog Content -->
        <div class="mb-6">
          <p class="text-gray-700 dark:text-gray-300">
            Are you sure you want to clear all chat messages? This will permanently delete your entire conversation history.
          </p>
        </div>

        <!-- Dialog Actions -->
        <div class="flex space-x-3 justify-end">
          <button
            type="button"
            on:click={cancelClear}
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 rounded-lg transition-colors focus:ring-2 focus:ring-gray-500 focus:border-gray-500"
          >
            Cancel
          </button>
          <button
            type="button"
            on:click={confirmClear}
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 dark:bg-red-600 dark:hover:bg-red-700 border border-red-600 dark:border-red-600 rounded-lg transition-colors focus:ring-2 focus:ring-red-500 focus:border-red-500"
          >
            Clear Chat
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
