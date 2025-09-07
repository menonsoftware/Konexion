<script>
	export let title = 'Something went wrong';
	export let message = 'An unexpected error occurred';
	export let onRetry = null;
</script>

<div class="flex items-center justify-center p-8">
	<div class="max-w-md text-center">
		<div class="mb-4">
			<svg class="mx-auto h-16 w-16 text-red-500" fill="currentColor" viewBox="0 0 20 20">
				<path
					fill-rule="evenodd"
					d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
					clip-rule="evenodd"
				/>
			</svg>
		</div>

		<h2 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">
			{title}
		</h2>

		<p class="mb-6 text-gray-600 dark:text-gray-300">
			{message}
		</p>

		{#if onRetry}
			<button
				on:click={onRetry}
				class="rounded-lg bg-blue-500 px-4 py-2 text-white transition-colors hover:bg-blue-600"
			>
				Try Again
			</button>
		{/if}
	</div>
</div>
