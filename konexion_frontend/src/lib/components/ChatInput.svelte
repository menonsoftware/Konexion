<script>
	import { selectedModel, availableModels, isLoading, maxTokens } from '$lib/stores.js';
	import { wsService } from '$lib/websocket.js';
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	let message = '';
	let textarea;
	let showModelDropdown = false;
	let modelSearchQuery = '';
	let filteredModels = [];
	let selectedModelIndex = -1;
	let selectedImages = [];
	let fileInput;

	// Filter models based on search query
	$: filteredModels = $availableModels.filter((model) => {
		const query = modelSearchQuery.toLowerCase();
		return (
			model.model_id.toLowerCase().includes(query) || model.owned_by.toLowerCase().includes(query)
		);
	});

	// Check if current model supports vision
	$: supportsVision =
		$selectedModel &&
		($selectedModel.toLowerCase().includes('gemma3') ||
			$selectedModel.toLowerCase().includes('scout') ||
			$selectedModel.toLowerCase().includes('maverick') ||
			$selectedModel.toLowerCase().includes('llava') ||
			$selectedModel.toLowerCase().includes('bakllava') ||
			$selectedModel.toLowerCase().includes('llava-phi3') ||
			$selectedModel.toLowerCase().includes('moondream') ||
			$selectedModel.toLowerCase().includes('vision') ||
			$selectedModel.toLowerCase().includes('llama-3.2-11b-vision-preview') ||
			$selectedModel.toLowerCase().includes('llama-3.2-90b-vision-preview') ||
			$selectedModel.toLowerCase().includes('gpt-4-vision-preview') ||
			$selectedModel.toLowerCase().includes('gpt-4o'));

	// Reset selected index when filtered models change
	$: if (filteredModels) {
		selectedModelIndex = -1;
	}

	function handleSubmit(event) {
		event.preventDefault();

		if ((message.trim() || selectedImages.length > 0) && !$isLoading && $selectedModel) {
			wsService.sendMessage(message.trim(), $selectedModel, selectedImages, $maxTokens);
			message = '';
			selectedImages = [];
			adjustTextareaHeight();
		}
	}

	function handleImageSelect() {
		fileInput.click();
	}

	function handleFileChange(event) {
		const files = Array.from(event.target.files);
		const imageFiles = files.filter((file) => file.type.startsWith('image/'));

		if (files.length > imageFiles.length) {
			alert('Only image files are supported. Non-image files have been filtered out.');
		}

		imageFiles.forEach((file) => {
			if (file.size > 10 * 1024 * 1024) {
				// 10MB limit
				alert(`Image "${file.name}" is too large. Maximum size is 10MB.`);
				return;
			}

			if (selectedImages.length >= 5) {
				// Limit to 5 images
				alert('You can attach up to 5 images at once.');
				return;
			}

			const reader = new FileReader();
			reader.onload = (e) => {
				const imageData = {
					id: Date.now() + Math.random(),
					file: file,
					name: file.name,
					type: file.type,
					size: file.size,
					dataUrl: e.target.result
				};
				selectedImages = [...selectedImages, imageData];
			};
			reader.onerror = () => {
				alert(`Failed to read image "${file.name}". Please try again.`);
			};
			reader.readAsDataURL(file);
		});

		// Reset file input
		event.target.value = '';
	}

	function removeImage(imageId) {
		selectedImages = selectedImages.filter((img) => img.id !== imageId);
	}

	function handleKeyDown(event) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSubmit(event);
		}
	}

	function handleSearchKeyDown(event) {
		if (!showModelDropdown || filteredModels.length === 0) return;

		switch (event.key) {
			case 'ArrowDown':
				event.preventDefault();
				selectedModelIndex = Math.min(selectedModelIndex + 1, filteredModels.length - 1);
				break;
			case 'ArrowUp':
				event.preventDefault();
				selectedModelIndex = Math.max(selectedModelIndex - 1, -1);
				break;
			case 'Enter':
				event.preventDefault();
				if (selectedModelIndex >= 0 && selectedModelIndex < filteredModels.length) {
					selectModel(filteredModels[selectedModelIndex]);
				}
				break;
			case 'Escape':
				event.preventDefault();
				showModelDropdown = false;
				modelSearchQuery = '';
				break;
		}
	}

	function adjustTextareaHeight() {
		if (textarea) {
			textarea.style.height = 'auto';
			textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
		}
	}

	function selectModel(model) {
		selectedModel.set(model.model_id);
		showModelDropdown = false;
		modelSearchQuery = '';
		selectedModelIndex = -1;
	}

	function toggleModelDropdown() {
		showModelDropdown = !showModelDropdown;
		if (showModelDropdown) {
			modelSearchQuery = '';
			// Focus search input after dropdown opens
			setTimeout(() => {
				const searchInput = document.getElementById('model-search');
				if (searchInput) searchInput.focus();
			}, 100);
		}
	}

	// Auto-adjust textarea height on input
	$: if (message !== undefined) {
		setTimeout(adjustTextareaHeight, 0);
	}

	// Close dropdown when clicking outside
	function handleClickOutside(event) {
		if (!event.target.closest('.model-selector')) {
			showModelDropdown = false;
			modelSearchQuery = '';
		}
	}
</script>

<svelte:window on:click={handleClickOutside} />

<!-- Hidden file input -->
<input
	bind:this={fileInput}
	type="file"
	accept="image/*"
	multiple
	on:change={handleFileChange}
	class="hidden"
	aria-label="Select images"
/>

<div
	class="border-t border-gray-300 bg-gray-100 px-4 py-4 sm:px-6 dark:border-gray-600 dark:bg-gray-800"
>
	<!-- Image previews -->
	{#if selectedImages.length > 0}
		<div class="mb-4">
			<div class="mb-2 text-sm text-gray-600 dark:text-gray-400">
				{selectedImages.length} image{selectedImages.length > 1 ? 's' : ''} attached:
			</div>
			<div class="flex flex-wrap gap-2">
				{#each selectedImages as image (image.id)}
					<div class="group relative">
						<img
							src={image.dataUrl}
							alt={image.name}
							class="h-20 w-20 rounded-lg border border-gray-300 object-cover transition-colors hover:border-blue-500 dark:border-gray-600 dark:hover:border-blue-400"
						/>
						<button
							type="button"
							on:click={() => removeImage(image.id)}
							class="absolute -top-2 -right-2 flex h-6 w-6 items-center justify-center rounded-full bg-red-500 text-xs text-white opacity-0 shadow-lg transition-opacity group-hover:opacity-100 hover:bg-red-600"
							aria-label="Remove {image.name}"
							title="Remove image"
						>
							×
						</button>
						<div
							class="bg-opacity-50 absolute right-0 bottom-0 left-0 truncate rounded-b-lg bg-black p-1 text-xs text-white"
						>
							{image.name}
						</div>
						<!-- File size indicator -->
						<div
							class="bg-opacity-50 absolute top-1 left-1 rounded bg-black px-1 text-xs text-white"
						>
							{(image.size / 1024).toFixed(0)}KB
						</div>
					</div>
				{/each}
			</div>
			<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
				{#if supportsVision}
					<span class="font-medium text-green-600 dark:text-green-400">✓ Vision model:</span> Images
					will be directly analyzed by the AI
				{:else}
					<span class="text-amber-600 dark:text-amber-400">⚠ Text-only model:</span> Images will be
					described to the AI for analysis
				{/if}
			</div>
		</div>
	{/if}
	<form on:submit={handleSubmit} class="flex items-end space-x-2 sm:space-x-4">
		<!-- Attachment buttons (hidden on mobile) -->
		<div class="hidden space-x-2 pb-2 sm:flex">
			<button
				type="button"
				on:click={handleImageSelect}
				class="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-200 hover:text-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300"
				title="Attach image"
				aria-label="Attach image"
			>
				<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
					<path
						fill-rule="evenodd"
						d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
						clip-rule="evenodd"
					/>
				</svg>
			</button>

			<button
				type="button"
				class="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-200 hover:text-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300"
				title="Attach file"
				aria-label="Attach file"
			>
				<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
					<path
						fill-rule="evenodd"
						d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z"
						clip-rule="evenodd"
					/>
				</svg>
			</button>
		</div>

		<!-- Message input -->
		<div class="relative flex-1">
			<!-- Mobile attachment button -->
			<button
				type="button"
				on:click={handleImageSelect}
				class="absolute top-1/2 left-2 -translate-y-1/2 transform p-1 text-gray-500 hover:text-gray-700 sm:hidden dark:text-gray-400 dark:hover:text-gray-300"
				title="Attach image"
				aria-label="Attach image"
			>
				<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
					<path
						fill-rule="evenodd"
						d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
						clip-rule="evenodd"
					/>
				</svg>
			</button>

			<textarea
				id="message-input"
				bind:this={textarea}
				bind:value={message}
				on:keydown={handleKeyDown}
				on:input={adjustTextareaHeight}
				placeholder="Ask anything..."
				disabled={$isLoading}
				class="w-full resize-none rounded-xl border border-gray-300 bg-white px-4 py-3 pl-10 text-gray-900 placeholder-gray-500 transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50 sm:pl-4 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
				rows="1"
				maxlength="2000"
			></textarea>

			<!-- Character count -->
			<div class="absolute right-2 -bottom-5 text-xs text-gray-400">
				{message.length}/2000
			</div>
		</div>

		<!-- Model selector and send button -->
		<div class="flex items-end space-x-2 pb-2">
			<!-- Model selector -->
			<div class="model-selector relative">
				<button
					type="button"
					on:click={toggleModelDropdown}
					class="flex items-center space-x-2 rounded-lg bg-gray-200 px-3 py-2 text-gray-800 transition-colors hover:bg-gray-300 disabled:opacity-50 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
					disabled={$isLoading}
					title="Select AI Model"
				>
					{#if $selectedModel}
						<span class="max-w-24 truncate text-sm font-medium sm:max-w-none" title={$selectedModel}
							>{$selectedModel}</span
						>
					{:else}
						<span class="text-sm text-gray-500">Model</span>
					{/if}
					<svg class="h-4 w-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
							clip-rule="evenodd"
						/>
					</svg>
				</button>

				{#if showModelDropdown}
					<div
						class="absolute right-0 bottom-full z-10 mb-2 w-80 rounded-lg border border-gray-300 bg-white shadow-lg sm:w-96 dark:border-gray-600 dark:bg-gray-800"
					>
						<!-- Search Header -->
						<div class="border-b border-gray-300 p-3 dark:border-gray-600">
							<div class="flex items-center space-x-2">
								<svg class="h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
									<path
										fill-rule="evenodd"
										d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
										clip-rule="evenodd"
									/>
								</svg>
								<input
									id="model-search"
									type="text"
									placeholder="Search models..."
									bind:value={modelSearchQuery}
									on:keydown={handleSearchKeyDown}
									class="flex-1 border-none bg-transparent text-sm text-gray-900 placeholder-gray-400 outline-none dark:text-white dark:placeholder-gray-500"
								/>
								{#if modelSearchQuery}
									<button
										type="button"
										on:click={() => (modelSearchQuery = '')}
										class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
										aria-label="Clear search"
									>
										<svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
											<path
												fill-rule="evenodd"
												d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
												clip-rule="evenodd"
											/>
										</svg>
									</button>
								{/if}
							</div>
						</div>

						<!-- Models List -->
						<div class="max-h-48 overflow-y-auto sm:max-h-60">
							{#if filteredModels.length === 0}
								<div class="px-3 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
									{modelSearchQuery ? 'No models found' : 'Loading models...'}
								</div>
							{:else}
								{#each filteredModels as model, index (model.model_id)}
									<button
										type="button"
										on:click={() => selectModel(model)}
										class="group flex w-full items-center justify-between px-3 py-2 text-left transition-colors
                      {index === selectedModelIndex
											? 'bg-blue-50 dark:bg-blue-900/20'
											: 'hover:bg-gray-50 dark:hover:bg-gray-700'}"
									>
										<div class="min-w-0 flex-1">
											<div
												class="flex flex-wrap items-center gap-2 text-sm font-medium text-gray-900 dark:text-white"
											>
												<span class="break-words">{model.model_id}</span>
												<span
													class="inline-flex flex-shrink-0 items-center rounded-full bg-gray-100 px-1.5 py-0.5 text-xs font-medium text-gray-800 dark:bg-gray-700 dark:text-gray-200"
												>
													{model.client_type}
												</span>
												{#if model.model_id.toLowerCase().includes('gemma3') || model.model_id
														.toLowerCase()
														.includes('llava') || model.model_id
														.toLowerCase()
														.includes('scout') || model.model_id
														.toLowerCase()
														.includes('maverick') || model.model_id
														.toLowerCase()
														.includes('vision') || model.model_id
														.toLowerCase()
														.includes('llama-3.2-11b-vision-preview') || model.model_id
														.toLowerCase()
														.includes('llama-3.2-90b-vision-preview')}
													<span
														class="inline-flex flex-shrink-0 items-center rounded-full bg-green-100 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200"
													>
														👁️ Vision
													</span>
												{/if}
											</div>
											<div class="text-xs text-gray-500 dark:text-gray-400">
												{model.owned_by} • Max: {model.context_window.toLocaleString()}
											</div>
										</div>
										{#if $selectedModel === model.model_id}
											<svg
												class="h-4 w-4 flex-shrink-0 text-blue-500"
												fill="currentColor"
												viewBox="0 0 20 20"
											>
												<path
													fill-rule="evenodd"
													d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
													clip-rule="evenodd"
												/>
											</svg>
										{/if}
									</button>
								{/each}
							{/if}
						</div>
					</div>
				{/if}
			</div>

			<!-- Send button -->
			<button
				type="submit"
				disabled={(!message.trim() && selectedImages.length === 0) || $isLoading || !$selectedModel}
				class="rounded-xl bg-blue-500 p-3 text-white transition-colors hover:bg-blue-600 disabled:cursor-not-allowed disabled:bg-gray-300 dark:disabled:bg-gray-600"
				title="Send message"
			>
				{#if $isLoading}
					<svg class="h-5 w-5 animate-spin" fill="currentColor" viewBox="0 0 20 20">
						<path
							d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H8a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H12a1 1 0 110-2h4a1 1 0 011 1v4a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
						/>
					</svg>
				{:else}
					<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
						<path
							d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"
						/>
					</svg>
				{/if}
			</button>
		</div>
	</form>
</div>
