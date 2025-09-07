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
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" 
    on:click={close}
    on:keydown={(e) => e.key === 'Escape' && close()}
    role="dialog"
    aria-modal="true"
    aria-labelledby="shortcuts-title"
    tabindex="-1"
  >
    <div 
      class="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6" 
      role="document"
    >
      <div class="flex items-center justify-between mb-4">
        <h2 id="shortcuts-title" class="text-lg font-semibold text-gray-900 dark:text-white">
          Keyboard Shortcuts
        </h2>
        <button
          on:click={close}
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          aria-label="Close shortcuts dialog"
        >
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
      
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-gray-700 dark:text-gray-300">Focus message input</span>
          <kbd class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-xs rounded">Ctrl+Shift+K</kbd>
        </div>
        
        <div class="flex items-center justify-between">
          <span class="text-gray-700 dark:text-gray-300">Toggle dark mode</span>
          <kbd class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-xs rounded">Ctrl+Shift+D</kbd>
        </div>
        
        <div class="flex items-center justify-between">
          <span class="text-gray-700 dark:text-gray-300">Send message</span>
          <kbd class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-xs rounded">Enter</kbd>
        </div>
        
        <div class="flex items-center justify-between">
          <span class="text-gray-700 dark:text-gray-300">New line in message</span>
          <kbd class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-xs rounded">Shift+Enter</kbd>
        </div>
        
        <div class="flex items-center justify-between">
          <span class="text-gray-700 dark:text-gray-300">Navigate model dropdown</span>
          <kbd class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-xs rounded">↑/↓ Arrow</kbd>
        </div>
        
        <div class="flex items-center justify-between">
          <span class="text-gray-700 dark:text-gray-300">Show this help</span>
          <kbd class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-xs rounded">?</kbd>
        </div>
      </div>
    </div>
  </div>
{/if}
