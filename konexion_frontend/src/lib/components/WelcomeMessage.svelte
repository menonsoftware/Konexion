<script>
  import { onMount } from 'svelte';
  import konexionLogo from '$lib/assets/konexion.png';
  
  let currentTime = '';
  let weatherInfo = '';
  
  onMount(() => {
    // Update time
    const updateTime = () => {
      const now = new Date();
      currentTime = now.toLocaleString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };
    
    updateTime();
    const timeInterval = setInterval(updateTime, 60000); // Update every minute
    
    // Simple weather info (you could integrate with a weather API)
    weatherInfo = 'Welcome to your AI assistant';
    
    return () => {
      clearInterval(timeInterval);
    };
  });
</script>

<div class="text-center py-8 fade-in">
  <div class="mb-6">
    <div class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 overflow-hidden bg-white dark:bg-gray-100 p-2">
      <img src={konexionLogo} alt="Konexion Logo" class="w-full h-full object-contain" />
    </div>
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
      WebKonexion
    </h2>
    <p class="text-gray-700 dark:text-gray-300 text-lg mb-4">
      Converse Smarter. Solve Faster.
    </p>
  </div>
  
  <div class="bg-gray-50 dark:bg-gray-700 rounded-xl p-6 shadow-sm border border-gray-300 dark:border-gray-600 max-w-md mx-auto">
    <div class="text-sm text-gray-600 dark:text-gray-400 mb-2">
      {currentTime}
    </div>
    <div class="text-sm text-blue-600 dark:text-blue-400 font-medium">
      {weatherInfo}
    </div>
  </div>
  
  <div class="mt-6 text-sm text-gray-600 dark:text-gray-400">
    Send a message to get started
  </div>
</div>
