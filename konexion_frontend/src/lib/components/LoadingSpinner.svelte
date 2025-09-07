<script>
	export let message = 'Loading...';
</script>

<div class="flex items-center justify-center p-8">
	<div class="text-center">
		<div
			class="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"
		></div>
		<p class="text-gray-600 dark:text-gray-300">{message}</p>
	</div>
</div>
