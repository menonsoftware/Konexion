<script>
  let { children } = $props();
</script>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
  <div class="max-w-6xl mx-auto">
    {@render children?.()}
  </div>
</div>
