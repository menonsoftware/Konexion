<script>
  import { maxTokens } from '$lib/stores.js';
  import { config } from '$lib/config.js';
  
  let showDropdown = $state(false);
  let customValue = $state('');
  let isCustomMode = $state(false);
  
  // Prop to control if label should be shown (for sidebar usage)
  let { showLabel = true } = $props();
  
  // Check if current value is in predefined options
  let isCustom = $derived(!config.ai.maxTokensOptions.some(option => option.value === $maxTokens) || isCustomMode);
  
  // Update custom value when maxTokens changes
  $effect(() => {
    if (isCustom && !isCustomMode) {
      customValue = $maxTokens.toString();
    }
  });
  
  function selectOption(value) {
    maxTokens.set(value);
    showDropdown = false;
    isCustomMode = false;
    customValue = '';
  }
  
  function handleCustomInput(event) {
    const value = parseInt(event.target.value);
    if (!isNaN(value) && value > 0) {
      maxTokens.set(value);
    }
  }
  
  function toggleCustom() {
    if (isCustomMode) {
      // Exit custom mode - find closest predefined option or use default
      const closest = config.ai.maxTokensOptions.reduce((prev, curr) => 
        Math.abs(curr.value - $maxTokens) < Math.abs(prev.value - $maxTokens) ? curr : prev
      );
      maxTokens.set(closest.value);
      isCustomMode = false;
    } else {
      // Enter custom mode
      isCustomMode = true;
      customValue = $maxTokens.toString();
      showDropdown = false;
    }
  }
  
  function handleClickOutside(event) {
    if (!event.target.closest('.max-tokens-selector')) {
      showDropdown = false;
    }
  }
</script>

<svelte:window onclick={handleClickOutside} />

<div class="max-tokens-selector relative">
  <div class="flex items-center space-x-2">
    {#if showLabel}
      <span class="text-xs text-gray-600 dark:text-gray-400 flex-shrink-0">
        Max tokens:
      </span>
    {/if}
    
    {#if isCustom}
      <input
        type="number"
        bind:value={customValue}
        oninput={handleCustomInput}
        onblur={() => {
          if (!customValue || parseInt(customValue) <= 0) {
            maxTokens.set(config.ai.defaultMaxTokens);
            isCustomMode = false;
          }
        }}
        min="1"
        max="32768"
        class="w-20 px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
        placeholder="2048"
      />
    {:else}
      <button
        type="button"
        onclick={() => showDropdown = !showDropdown}
        class="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors flex items-center space-x-1"
      >
        <span>{$maxTokens.toLocaleString()}</span>
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
    {/if}
    
    <button
      type="button"
      onclick={toggleCustom}
      class="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-500 transition-colors"
      title={isCustomMode ? 'Use preset values' : 'Enter custom value'}
      aria-label={isCustomMode ? 'Use preset values' : 'Enter custom value'}
    >
      {isCustomMode ? '📋' : '✏️'}
    </button>
  </div>
  
  {#if showDropdown && !isCustom}
    <div class="absolute top-full mt-1 right-0 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg z-50 min-w-32">
      <div class="py-1">
        {#each config.ai.maxTokensOptions as option (option.value)}
          <button
            type="button"
            onclick={() => selectOption(option.value)}
            class="w-full px-3 py-2 text-left text-xs hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center justify-between
              {$maxTokens === option.value ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' : 'text-gray-900 dark:text-white'}"
          >
            <span>{option.label}</span>
            {#if $maxTokens === option.value}
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            {/if}
          </button>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  input[type="number"]::-webkit-outer-spin-button,
  input[type="number"]::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  
  input[type="number"] {
    -moz-appearance: textfield;
    appearance: textfield;
  }
</style>
