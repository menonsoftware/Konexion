<script>
	import { onMount, tick } from 'svelte';
	import { browser } from '$app/environment';

	export let show = false;
	export let title = '';
	export let description = '';
	export let content = '';
	export let onConfirm = null;
	export let onCancel = null;
	export let confirmText = 'Confirm';
	export let cancelText = 'Cancel';
	export let confirmClass =
		'px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 border border-blue-600 rounded-lg transition-colors focus:ring-2 focus:ring-blue-500 focus:border-blue-500';
	export let cancelClass =
		'px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 rounded-lg transition-colors focus:ring-2 focus:ring-gray-500 focus:border-gray-500';
	export let icon = null;

	let confirmButtonRef;

	function handleKeydown(event) {
		if (!show) return;
		if (event.key === 'Escape') {
			handleCancel();
		} else if (event.key === 'Enter') {
			event.preventDefault();
			handleConfirm();
		}
	}

	function handleConfirm() {
		if (onConfirm) onConfirm();
		show = false;
	}

	function handleCancel() {
		if (onCancel) onCancel();
		show = false;
	}

	function handleBackdropClick(event) {
		if (event.target === event.currentTarget) {
			handleCancel();
		}
	}

	// Focus the confirm button when modal opens
	$: if (show && browser && confirmButtonRef) {
		tick().then(() => {
			if (confirmButtonRef && typeof confirmButtonRef.focus === 'function') {
				confirmButtonRef.focus();
			}
		});
	}

	onMount(() => {
		if (browser) {
			const handleGlobalKeydown = (event) => handleKeydown(event);
			document.addEventListener('keydown', handleGlobalKeydown);
			return () => document.removeEventListener('keydown', handleGlobalKeydown);
		}
	});
</script>

{#if show}
	<!-- Modal Backdrop -->
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div
		class="bg-opacity-50 fixed inset-0 z-[9999] flex items-center justify-center bg-black p-4"
		on:click={handleBackdropClick}
	>
		<!-- Modal Content -->
		<div
			class="w-full max-w-md rounded-lg border border-gray-200 bg-white p-6 shadow-xl dark:border-gray-600 dark:bg-gray-800"
			role="dialog"
			aria-modal="true"
			aria-labelledby={title ? 'modal-title' : undefined}
		>
			<!-- Modal Header -->
			{#if title || icon}
				<div class="mb-4 flex items-center space-x-3">
					{#if icon}
						<div
							class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full {icon.bgClass ||
								'bg-gray-100 dark:bg-gray-700'}"
						>
							<!-- eslint-disable-next-line svelte/no-at-html-tags -->
							{@html icon.svg}
						</div>
					{/if}
					{#if title}
						<div>
							<h3 id="modal-title" class="text-lg font-semibold text-gray-900 dark:text-white">
								{title}
							</h3>
							{#if description}
								<p class="text-sm text-gray-500 dark:text-gray-400">{description}</p>
							{/if}
						</div>
					{/if}
				</div>
			{/if}

			<!-- Modal Content -->
			{#if content}
				<div class="mb-6">
					<!-- eslint-disable-next-line svelte/no-at-html-tags -->
					{@html content}
				</div>
			{/if}

			<!-- Modal Actions -->
			<div class="flex justify-end space-x-3">
				<button type="button" on:click={handleCancel} class={cancelClass}>
					{cancelText}
				</button>
				<button
					bind:this={confirmButtonRef}
					type="button"
					on:click={handleConfirm}
					class={confirmClass}
				>
					{confirmText}
				</button>
			</div>
		</div>
	</div>
{/if}
