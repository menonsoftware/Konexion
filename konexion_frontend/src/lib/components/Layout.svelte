<script>
	let { children } = $props();
</script>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="mx-auto max-w-6xl">
		{@render children?.()}
	</div>
</div>
