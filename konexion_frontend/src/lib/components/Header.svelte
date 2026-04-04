<script>
	import { isDarkMode, isConnected } from '$lib/stores.js';
	import { user, logout } from '$lib/auth.js';
	import KeyboardShortcuts from './KeyboardShortcuts.svelte';
	import RefreshModelsButton from './RefreshModelsButton.svelte';
	import konexionLogo from '$lib/assets/konexion.png';

	let showShortcuts = false;
	let showUserMenu = false;

	function toggleTheme() {
		isDarkMode.toggle();
	}

	function showHelp() {
		showShortcuts = true;
	}

	function toggleUserMenu() {
		showUserMenu = !showUserMenu;
	}

	function closeUserMenu() {
		showUserMenu = false;
	}

	async function handleLogout() {
		showUserMenu = false;
		await logout();
	}

	/** Initials fallback when no avatar_url is present */
	function initials(name) {
		if (!name) return '?';
		return name
			.split(' ')
			.map((w) => w[0])
			.slice(0, 2)
			.join('')
			.toUpperCase();
	}
</script>

<header
	class="border-b border-gray-300 bg-gray-100 px-4 py-4 sm:px-6 dark:border-gray-600 dark:bg-gray-800"
>
	<div class="flex items-center justify-between">
		<!-- Logo and title -->
		<div class="flex items-center space-x-3 sm:space-x-4">
			<div class="flex items-center space-x-2">
				<div class="flex h-8 w-8 items-center justify-center overflow-hidden rounded-lg">
					<img src={konexionLogo} alt="Konexion Logo" class="h-full w-full object-contain" />
				</div>
				<div>
					<h1 class="text-lg font-semibold text-gray-900 sm:text-xl dark:text-white">
						WebKonexion
					</h1>
					<div class="flex items-center space-x-1">
						<div class="h-2 w-2 rounded-full {$isConnected ? 'bg-green-500' : 'bg-red-500'}"></div>
						<span class="text-xs text-gray-600 dark:text-gray-400">
							{$isConnected ? 'Connected' : 'Disconnected'}
						</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Actions -->
		<div class="flex items-center space-x-2 sm:space-x-3">
			<!-- Refresh Models Button -->
			<RefreshModelsButton size="header" variant="ghost" showText={false} />

			<button
				on:click={showHelp}
				class="rounded-lg bg-gray-200 p-2 transition-colors hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500"
				aria-label="Show keyboard shortcuts"
				title="Keyboard shortcuts"
			>
				<svg
					class="h-5 w-5 text-gray-700 dark:text-gray-300"
					fill="currentColor"
					viewBox="0 0 20 20"
				>
					<path
						fill-rule="evenodd"
						d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z"
						clip-rule="evenodd"
					/>
				</svg>
			</button>

			<button
				on:click={toggleTheme}
				class="rounded-lg bg-gray-200 p-2 transition-colors hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500"
				aria-label="Toggle theme"
			>
				{#if $isDarkMode}
					<!-- Sun icon for light mode -->
					<svg class="h-5 w-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
							clip-rule="evenodd"
						/>
					</svg>
				{:else}
					<!-- Moon icon for dark mode -->
					<svg class="h-5 w-5 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
						<path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
					</svg>
				{/if}
			</button>

			<!-- User avatar + dropdown -->
			{#if $user}
				<div class="relative">
					<button
						on:click={toggleUserMenu}
						class="flex h-8 w-8 items-center justify-center overflow-hidden rounded-full ring-2 ring-transparent transition-all hover:ring-blue-500 focus:ring-blue-500 focus:outline-none"
						aria-label="User menu"
						aria-expanded={showUserMenu}
					>
						{#if $user.avatar_url}
							<img
								src={$user.avatar_url}
								alt={$user.name ?? $user.email}
								class="h-full w-full object-cover"
								referrerpolicy="no-referrer"
							/>
						{:else}
							<span
								class="flex h-full w-full items-center justify-center bg-blue-600 text-xs font-semibold text-white"
							>
								{initials($user.name)}
							</span>
						{/if}
					</button>

					{#if showUserMenu}
						<!-- Backdrop -->
						<!-- svelte-ignore a11y-no-static-element-interactions -->
						<div
							class="fixed inset-0 z-10"
							on:click={closeUserMenu}
							on:keydown={(e) => e.key === 'Escape' && closeUserMenu()}
						></div>

						<!-- Dropdown panel -->
						<div
							class="absolute right-0 z-20 mt-2 w-56 origin-top-right rounded-xl border border-gray-200 bg-white shadow-lg ring-1 ring-black/5 dark:border-gray-700 dark:bg-gray-800"
						>
							<!-- User info -->
							<div class="border-b border-gray-100 px-4 py-3 dark:border-gray-700">
								<p class="truncate text-sm font-semibold text-gray-900 dark:text-white">
									{$user.name ?? 'User'}
								</p>
								<p class="truncate text-xs text-gray-500 dark:text-gray-400">
									{$user.email}
								</p>
							</div>

							<!-- Logout -->
							<div class="p-1">
								<button
									on:click={handleLogout}
									class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-red-600 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
								>
									<svg
										class="h-4 w-4"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v1"
										/>
									</svg>
									Sign out
								</button>
							</div>
						</div>
					{/if}
				</div>
			{/if}
		</div>
	</div>
</header>

<KeyboardShortcuts bind:show={showShortcuts} />
