<script>
	// No props needed for this component
</script>

<div class="flex justify-start">
	<div class="flex max-w-2xl space-x-3">
		<!-- Bot avatar -->
		<div class="flex-shrink-0">
			<div
				class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600"
			>
				<svg class="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
					<path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
				</svg>
			</div>
		</div>

		<div class="flex flex-col items-start">
			<!-- Typing bubble -->
			<div
				class="rounded-2xl border border-gray-300 bg-gray-50 px-4 py-3 text-gray-900 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
			>
				<div class="flex items-center space-x-1">
					<div class="typing-dot"></div>
					<div class="typing-dot"></div>
					<div class="typing-dot"></div>
				</div>
			</div>

			<!-- Timestamp -->
			<div class="mt-1 px-1 text-xs text-gray-600 dark:text-gray-400">Typing...</div>
		</div>
	</div>
</div>
