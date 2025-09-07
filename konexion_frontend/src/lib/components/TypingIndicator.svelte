<script>
  // No props needed for this component
</script>

<div class="flex justify-start">
  <div class="flex space-x-3 max-w-2xl">
    <!-- Bot avatar -->
    <div class="flex-shrink-0">
      <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
        <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      </div>
    </div>

    <div class="flex flex-col items-start">
      <!-- Typing bubble -->
      <div class="bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-2xl px-4 py-3">
        <div class="flex space-x-1 items-center">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>

      <!-- Timestamp -->
      <div class="text-xs text-gray-600 dark:text-gray-400 mt-1 px-1">
        Typing...
      </div>
    </div>
  </div>
</div>
