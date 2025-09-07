<script>
	import { isConnected } from '$lib/stores.js';
	import { wsService } from '$lib/websocket.js';

	function reconnect() {
		wsService.connect();
	}
</script>

{#if !$isConnected}
	<div
		class="border-t border-yellow-200 bg-yellow-50 px-4 py-3 dark:border-yellow-800 dark:bg-yellow-900"
	>
		<div class="flex items-center justify-between">
			<div class="flex items-center space-x-2">
				<svg class="h-5 w-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
					<path
						fill-rule="evenodd"
						d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
						clip-rule="evenodd"
					/>
				</svg>
				<span class="text-sm font-medium text-yellow-800 dark:text-yellow-200">
					Connection Lost
				</span>
				<span class="text-sm text-yellow-600 dark:text-yellow-300">
					Check your internet connection or backend server
				</span>
			</div>

			<button
				on:click={reconnect}
				class="rounded-md bg-yellow-100 px-3 py-1 text-sm text-yellow-800 transition-colors hover:bg-yellow-200 dark:bg-yellow-800 dark:text-yellow-200 dark:hover:bg-yellow-700"
			>
				Reconnect
			</button>
		</div>
	</div>
{/if}
