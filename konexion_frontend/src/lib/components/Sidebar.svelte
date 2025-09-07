<script>
  import { maxTokens } from '$lib/stores.js';
  import MaxTokensSelector from './MaxTokensSelector.svelte';
  
  let { isOpen = false, onToggle } = $props();
  
  function handleToggle() {
    if (onToggle) {
      onToggle();
    }
  }
  
  function handleClickOutside(event) {
    if (isOpen && !event.target.closest('.sidebar-content') && !event.target.closest('.sidebar-toggle')) {
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
  class="sidebar-toggle fixed top-20 right-4 z-30 p-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200"
  title={isOpen ? 'Close sidebar' : 'Open settings'}
  aria-label={isOpen ? 'Close sidebar' : 'Open settings'}
>
  <svg 
    class="w-5 h-5 text-gray-600 dark:text-gray-400 transition-transform duration-200 {isOpen ? 'rotate-180' : ''}" 
    fill="none" 
    stroke="currentColor" 
    viewBox="0 0 24 24"
  >
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.5 6L9 7.5 6 10.5m0 0l3 3L10.5 15M6 10.5h14.25" />
  </svg>
</button>

<!-- Sidebar Overlay -->
{#if isOpen}
  <div class="fixed inset-0 bg-black bg-opacity-50 z-20 transition-opacity duration-200"></div>
{/if}

<!-- Sidebar Content -->
<div class="sidebar-content fixed top-0 right-0 h-full w-80 bg-white dark:bg-gray-800 border-l border-gray-300 dark:border-gray-600 shadow-2xl z-25 transform transition-transform duration-300 ease-in-out {isOpen ? 'translate-x-0' : 'translate-x-full'}">
  <div class="flex flex-col h-full">
    <!-- Sidebar Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Settings</h3>
      <button
        type="button"
        onclick={handleToggle}
        class="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
        title="Close sidebar"
        aria-label="Close sidebar"
      >
        <svg class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    
    <!-- Sidebar Content -->
    <div class="flex-1 p-4 overflow-y-auto">
      <div class="space-y-6">
        <!-- AI Settings Section -->
        <div>
          <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">AI Configuration</h4>
          <div class="space-y-3">
            <!-- Max Tokens Setting -->
            <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
              <div class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max Tokens
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mb-2">
                Maximum number of tokens to generate in the response.
              </div>
              <MaxTokensSelector showLabel={false} />
            </div>
            
            <!-- Current Token Value Display -->
            <div class="text-xs text-gray-500 dark:text-gray-400">
              Current: <span class="font-mono text-blue-600 dark:text-blue-400">{$maxTokens.toLocaleString()}</span> tokens
            </div>
          </div>
        </div>
        
        <!-- Future Settings Placeholder -->
        <div>
          <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">Advanced</h4>
          <div class="text-xs text-gray-500 dark:text-gray-400">
            Additional settings coming soon...
          </div>
        </div>
      </div>
    </div>
    
    <!-- Sidebar Footer -->
    <div class="p-4 border-t border-gray-200 dark:border-gray-700">
      <div class="text-xs text-gray-500 dark:text-gray-400 text-center">
        Use <kbd class="px-1 py-0.5 bg-gray-200 dark:bg-gray-600 rounded text-xs">Ctrl+,</kbd> to toggle this panel
      </div>
    </div>
  </div>
</div>

<style>
  kbd {
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
  }
</style>
