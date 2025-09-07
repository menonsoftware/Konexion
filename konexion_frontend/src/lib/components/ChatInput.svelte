<script>
  import { selectedModel, availableModels, isLoading } from '$lib/stores.js';
  import { wsService } from '$lib/websocket.js';
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  let message = '';
  let textarea;
  let showModelDropdown = false;
  let modelSearchQuery = '';
  let filteredModels = [];
  let selectedModelIndex = -1;
  
  // Filter models based on search query
  $: filteredModels = $availableModels.filter(model => {
    const query = modelSearchQuery.toLowerCase();
    return (
      model.model_id.toLowerCase().includes(query) ||
      model.owned_by.toLowerCase().includes(query)
    );
  });
  
  // Reset selected index when filtered models change
  $: if (filteredModels) {
    selectedModelIndex = -1;
  }
  
  function handleSubmit(event) {
    event.preventDefault();
    
    if (message.trim() && !$isLoading && $selectedModel) {
      wsService.sendMessage(message.trim(), $selectedModel);
      message = '';
      adjustTextareaHeight();
    }
  }
  
  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit(event);
    }
  }
  
  function handleSearchKeyDown(event) {
    if (!showModelDropdown || filteredModels.length === 0) return;
    
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        selectedModelIndex = Math.min(selectedModelIndex + 1, filteredModels.length - 1);
        break;
      case 'ArrowUp':
        event.preventDefault();
        selectedModelIndex = Math.max(selectedModelIndex - 1, -1);
        break;
      case 'Enter':
        event.preventDefault();
        if (selectedModelIndex >= 0 && selectedModelIndex < filteredModels.length) {
          selectModel(filteredModels[selectedModelIndex]);
        }
        break;
      case 'Escape':
        event.preventDefault();
        showModelDropdown = false;
        modelSearchQuery = '';
        break;
    }
  }
  
  function adjustTextareaHeight() {
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  }
  
  function selectModel(model) {
    selectedModel.set(model.model_id);
    showModelDropdown = false;
    modelSearchQuery = '';
    selectedModelIndex = -1;
  }
  
  function toggleModelDropdown() {
    showModelDropdown = !showModelDropdown;
    if (showModelDropdown) {
      modelSearchQuery = '';
      // Focus search input after dropdown opens
      setTimeout(() => {
        const searchInput = document.getElementById('model-search');
        if (searchInput) searchInput.focus();
      }, 100);
    }
  }
  
  // Auto-adjust textarea height on input
  $: if (message !== undefined) {
    setTimeout(adjustTextareaHeight, 0);
  }
  
  // Close dropdown when clicking outside
  function handleClickOutside(event) {
    if (!event.target.closest('.model-selector')) {
      showModelDropdown = false;
      modelSearchQuery = '';
    }
  }
</script>

<svelte:window on:click={handleClickOutside} />

<div class="bg-gray-100 dark:bg-gray-800 border-t border-gray-300 dark:border-gray-600 px-4 sm:px-6 py-4">
  <form on:submit={handleSubmit} class="flex items-end space-x-2 sm:space-x-4">
    <!-- Attachment buttons (hidden on mobile) -->
    <div class="hidden sm:flex space-x-2 pb-2">
      <button
        type="button"
        class="p-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        title="Attach image"
        aria-label="Attach image"
      >
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
        </svg>
      </button>
      
      <button
        type="button"
        class="p-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        title="Attach file"
        aria-label="Attach file"
      >
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
    
    <!-- Message input -->
    <div class="flex-1 relative">
      <textarea
        id="message-input"
        bind:this={textarea}
        bind:value={message}
        on:keydown={handleKeyDown}
        on:input={adjustTextareaHeight}
        placeholder="Ask anything..."
        disabled={$isLoading}
        class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        rows="1"
        maxlength="2000"
      ></textarea>
      
      <!-- Character count -->
      <div class="absolute -bottom-5 right-2 text-xs text-gray-400">
        {message.length}/2000
      </div>
    </div>
    
    <!-- Model selector and send button -->
    <div class="flex items-end space-x-2 pb-2">
      <!-- Model selector -->
      <div class="relative model-selector">
        <button
          type="button"
          on:click={toggleModelDropdown}
          class="flex items-center space-x-2 px-3 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
          disabled={$isLoading}
          title="Select AI Model"
        >
          {#if $selectedModel}
            <span class="text-sm font-medium max-w-16 sm:max-w-none truncate">{$selectedModel}</span>
          {:else}
            <span class="text-sm text-gray-500">Model</span>
          {/if}
          <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
        
        {#if showModelDropdown}
          <div class="absolute bottom-full mb-2 right-0 w-72 sm:w-80 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg z-10">
            <!-- Search Header -->
            <div class="p-3 border-b border-gray-300 dark:border-gray-600">
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                </svg>
                <input
                  id="model-search"
                  type="text"
                  placeholder="Search models..."
                  bind:value={modelSearchQuery}
                  on:keydown={handleSearchKeyDown}
                  class="flex-1 text-sm bg-transparent border-none outline-none text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                />
                {#if modelSearchQuery}
                  <button 
                    type="button" 
                    on:click={() => modelSearchQuery = ''}
                    class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    aria-label="Clear search"
                  >
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                  </button>
                {/if}
              </div>
            </div>
            
            <!-- Models List -->
            <div class="max-h-48 sm:max-h-60 overflow-y-auto">
              {#if filteredModels.length === 0}
                <div class="px-3 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                  {modelSearchQuery ? 'No models found' : 'Loading models...'}
                </div>
              {:else}
                {#each filteredModels as model, index (model.model_id)}
                  <button
                    type="button"
                    on:click={() => selectModel(model)}
                    class="w-full px-3 py-2 text-left flex items-center justify-between group transition-colors
                      {index === selectedModelIndex 
                        ? 'bg-blue-50 dark:bg-blue-900/20' 
                        : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                      }"
                  >
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-medium text-gray-900 dark:text-white truncate flex items-center gap-2">
                        {model.model_id}
                        <span class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                          {model.client_type}
                        </span>
                      </div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">
                        {model.owned_by} • Max: {model.context_window.toLocaleString()}
                      </div>
                    </div>
                    {#if $selectedModel === model.model_id}
                      <svg class="w-4 h-4 text-blue-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                      </svg>
                    {/if}
                  </button>
                {/each}
              {/if}
            </div>
          </div>
        {/if}
      </div>
      
      <!-- Send button -->
      <button
        type="submit"
        disabled={!message.trim() || $isLoading || !$selectedModel}
        class="p-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 dark:disabled:bg-gray-600 text-white rounded-xl transition-colors disabled:cursor-not-allowed"
        title="Send message"
      >
        {#if $isLoading}
          <svg class="w-5 h-5 animate-spin" fill="currentColor" viewBox="0 0 20 20">
            <path d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H8a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H12a1 1 0 110-2h4a1 1 0 011 1v4a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" />
          </svg>
        {:else}
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
          </svg>
        {/if}
      </button>
    </div>
  </form>
</div>
