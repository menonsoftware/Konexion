<script>
  export let title = 'Something went wrong';
  export let message = 'An unexpected error occurred';
  export let onRetry = null;
</script>

<div class="flex items-center justify-center p-8">
  <div class="text-center max-w-md">
    <div class="mb-4">
      <svg class="w-16 h-16 text-red-500 mx-auto" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
    </div>
    
    <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
      {title}
    </h2>
    
    <p class="text-gray-600 dark:text-gray-300 mb-6">
      {message}
    </p>
    
    {#if onRetry}
      <button
        on:click={onRetry}
        class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
      >
        Try Again
      </button>
    {/if}
  </div>
</div>
