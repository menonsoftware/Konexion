<script>
  import { isDarkMode, isConnected } from '$lib/stores.js';
  import KeyboardShortcuts from './KeyboardShortcuts.svelte';
  import konexionLogo from '$lib/assets/konexion.png';
  
  let showShortcuts = false;
  
  function toggleTheme() {
    isDarkMode.toggle();
  }
  
  function showHelp() {
    showShortcuts = true;
  }
</script>

<header class="bg-gray-100 dark:bg-gray-800 border-b border-gray-300 dark:border-gray-600 px-4 sm:px-6 py-4">
  <div class="flex items-center justify-between">
    <!-- Logo and title -->
    <div class="flex items-center space-x-3 sm:space-x-4">
      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 rounded-lg flex items-center justify-center overflow-hidden">
          <img src={konexionLogo} alt="Konexion Logo" class="w-full h-full object-contain" />
        </div>
        <div>
          <h1 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">WebKonexion</h1>
          <div class="flex items-center space-x-1">
            <div class="w-2 h-2 rounded-full {$isConnected ? 'bg-green-500' : 'bg-red-500'}"></div>
            <span class="text-xs text-gray-600 dark:text-gray-400">
              {$isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Theme toggle and help -->
    <div class="flex items-center space-x-2 sm:space-x-4">
      <button
        on:click={showHelp}
        class="p-2 rounded-lg bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 transition-colors"
        aria-label="Show keyboard shortcuts"
        title="Keyboard shortcuts"
      >
        <svg class="w-5 h-5 text-gray-700 dark:text-gray-300" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
        </svg>
      </button>
      
      <button
        on:click={toggleTheme}
        class="p-2 rounded-lg bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 transition-colors"
        aria-label="Toggle theme"
      >
        {#if $isDarkMode}
          <!-- Sun icon for light mode -->
          <svg class="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
          </svg>
        {:else}
          <!-- Moon icon for dark mode -->
          <svg class="w-5 h-5 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
            <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
          </svg>
        {/if}
      </button>
    </div>
  </div>
</header>

<KeyboardShortcuts bind:show={showShortcuts} />
