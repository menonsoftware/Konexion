<script>
	export let code = '';
	export let language = '';

	import hljs from 'highlight.js/lib/core';
	import { onMount } from 'svelte';

	// Import common languages
	import javascript from 'highlight.js/lib/languages/javascript';
	import python from 'highlight.js/lib/languages/python';
	import typescript from 'highlight.js/lib/languages/typescript';
	import css from 'highlight.js/lib/languages/css';
	import html from 'highlight.js/lib/languages/xml';
	import json from 'highlight.js/lib/languages/json';
	import bash from 'highlight.js/lib/languages/bash';
	import sql from 'highlight.js/lib/languages/sql';
	import java from 'highlight.js/lib/languages/java';
	import cpp from 'highlight.js/lib/languages/cpp';
	import csharp from 'highlight.js/lib/languages/csharp';
	import php from 'highlight.js/lib/languages/php';
	import go from 'highlight.js/lib/languages/go';
	import rust from 'highlight.js/lib/languages/rust';
	// PowerShell support - will be registered if available
	let powershell;

	let copied = false;
	let copyTimeout;
	let highlightedCode = '';

	onMount(() => {
		// Register languages
		hljs.registerLanguage('javascript', javascript);
		hljs.registerLanguage('js', javascript);
		hljs.registerLanguage('python', python);
		hljs.registerLanguage('py', python);
		hljs.registerLanguage('typescript', typescript);
		hljs.registerLanguage('ts', typescript);
		hljs.registerLanguage('css', css);
		hljs.registerLanguage('html', html);
		hljs.registerLanguage('xml', html);
		hljs.registerLanguage('json', json);
		hljs.registerLanguage('bash', bash);
		hljs.registerLanguage('sh', bash);
		hljs.registerLanguage('shell', bash);
		hljs.registerLanguage('sql', sql);
		hljs.registerLanguage('java', java);
		hljs.registerLanguage('cpp', cpp);
		hljs.registerLanguage('c++', cpp);
		hljs.registerLanguage('csharp', csharp);
		hljs.registerLanguage('c#', csharp);
		hljs.registerLanguage('php', php);
		hljs.registerLanguage('go', go);
		hljs.registerLanguage('rust', rust);

		// Try to load PowerShell support
		try {
			import('highlight.js/lib/languages/powershell')
				.then((module) => {
					powershell = module.default;
					hljs.registerLanguage('powershell', powershell);
					hljs.registerLanguage('ps1', powershell);
					hljs.registerLanguage('posh', powershell);
				})
				.catch((err) => {
					console.log('PowerShell highlighting not available:', err.message);
					// Fallback: use bash for PowerShell
					hljs.registerLanguage('powershell', bash);
					hljs.registerLanguage('ps1', bash);
					hljs.registerLanguage('posh', bash);
				});
		} catch (error) {
			console.log('PowerShell highlighting not available:', error.message);
			// Fallback: use bash for PowerShell
			hljs.registerLanguage('powershell', bash);
			hljs.registerLanguage('ps1', bash);
			hljs.registerLanguage('posh', bash);
		}

		// Highlight the code
		try {
			// Ensure code is a string and clean up any [object Object] references
			let cleanCode = typeof code === 'string' ? code : String(code);
			cleanCode = cleanCode.replace(/\[object Object\]/g, 'appropriate_command');

			if (language && hljs.getLanguage(language)) {
				const result = hljs.highlight(cleanCode, { language: language });
				highlightedCode = result.value;
			} else if (cleanCode.trim()) {
				// Auto-detect language only if code is not empty
				const result = hljs.highlightAuto(cleanCode);
				highlightedCode = result.value;
			} else {
				highlightedCode = cleanCode;
			}
		} catch (error) {
			console.warn('Failed to highlight code:', error);
			let fallbackCode = typeof code === 'string' ? code : String(code);
			fallbackCode = fallbackCode.replace(/\[object Object\]/g, 'appropriate_command');
			highlightedCode = fallbackCode; // Fallback to plain text
		}
	});

	// Re-highlight when code or language changes
	$: if (code || language) {
		try {
			// Ensure code is a string and clean up any [object Object] references
			let cleanCode = typeof code === 'string' ? code : String(code);
			cleanCode = cleanCode.replace(/\[object Object\]/g, 'appropriate_command');

			if (language && hljs.getLanguage(language)) {
				const result = hljs.highlight(cleanCode, { language: language });
				highlightedCode = result.value;
			} else if (cleanCode.trim()) {
				const result = hljs.highlightAuto(cleanCode);
				highlightedCode = result.value;
			} else {
				highlightedCode = cleanCode;
			}
		} catch (error) {
			let fallbackCode = typeof code === 'string' ? code : String(code);
			fallbackCode = fallbackCode.replace(/\[object Object\]/g, 'appropriate_command');
			highlightedCode = fallbackCode;
		}
	}

	async function copyToClipboard() {
		try {
			// Clean the code before copying
			let cleanCode = typeof code === 'string' ? code : String(code);
			cleanCode = cleanCode.replace(/\[object Object\]/g, 'appropriate_command');

			await navigator.clipboard.writeText(cleanCode);
			copied = true;

			// Clear any existing timeout
			if (copyTimeout) {
				clearTimeout(copyTimeout);
			}

			// Reset copied state after 2 seconds
			copyTimeout = setTimeout(() => {
				copied = false;
			}, 2000);
		} catch (err) {
			console.error('Failed to copy code:', err);
		}
	}

	// Clean up timeout on component destroy
	import { onDestroy } from 'svelte';
	onDestroy(() => {
		if (copyTimeout) {
			clearTimeout(copyTimeout);
		}
	});
</script>

<div class="group code-block relative">
	<!-- Language label and copy button header -->
	<div
		class="flex items-center justify-between rounded-t-lg border-t border-r border-l border-gray-300 bg-gray-100 px-4 py-2 dark:border-gray-600 dark:bg-gray-800"
	>
		<span class="text-xs font-medium tracking-wider text-gray-600 uppercase dark:text-gray-400">
			{language || 'text'}
		</span>

		<button
			on:click={copyToClipboard}
			class="flex items-center space-x-1 rounded bg-transparent px-2 py-1 text-xs text-gray-600 transition-all duration-200 hover:bg-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none dark:text-gray-300 dark:hover:bg-gray-700"
			title={copied ? 'Copied!' : 'Copy code to clipboard'}
			aria-label={copied ? 'Code copied to clipboard' : 'Copy code to clipboard'}
		>
			{#if copied}
				<!-- Check icon with animation -->
				<svg class="h-3 w-3 animate-pulse text-green-500" fill="currentColor" viewBox="0 0 20 20">
					<path
						fill-rule="evenodd"
						d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
						clip-rule="evenodd"
					/>
				</svg>
				<span class="font-medium text-green-500">Copied!</span>
			{:else}
				<!-- Copy icon -->
				<svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
					<path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
					<path
						d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"
					/>
				</svg>
				<span>Copy</span>
			{/if}
		</button>
	</div>

	<!-- Code content -->
	<pre
		class="m-0 overflow-x-auto rounded-b-lg border border-gray-300 bg-gray-50 p-4 text-sm leading-relaxed dark:border-gray-600 dark:bg-gray-900"><code
			class="language-{language}">{@html highlightedCode || code}</code
		></pre>
</div>

<style>
	.code-block {
		font-family: 'Fira Code', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
	}

	.code-block pre {
		/* Ensure proper scrolling for long lines */
		white-space: pre;
		word-wrap: normal;
		overflow-x: auto;
	}

	.code-block code {
		/* Reset any inherited styles */
		background: none;
		padding: 0;
		border: none;
		border-radius: 0;
		font-size: inherit;
		color: inherit;
	}
</style>
