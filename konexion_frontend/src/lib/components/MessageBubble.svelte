<script>
  export let message;
  
  import { marked } from 'marked';
  import { onMount } from 'svelte';
  import CodeBlock from './CodeBlock.svelte';
  
  let processedContent = [];
  let mounted = false;
  
  onMount(() => {
    mounted = true;
    
    const renderer = new marked.Renderer();
    
    renderer.codespan = function(code) {
      const safeCode = typeof code === 'string' ? code : String(code);
      return `<code class="inline-code bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm font-mono">${safeCode}</code>`;
    };
    
    // Don't override code block rendering - let parseContentToBlocks handle it
    // renderer.code is intentionally not overridden to preserve CodeBlock component usage
    
    marked.setOptions({
      breaks: true,
      gfm: true,
      renderer: renderer,
      pedantic: false,
      sanitize: false,
      smartypants: false,
      tokenizer: {
        // Custom tokenizer to handle inline code better
        codespan(src) {
          const match = src.match(/^(`+)([^\r]*?[^`])\1(?!`)/);
          if (match) {
            return {
              type: 'codespan',
              raw: match[0],
              text: match[2].trim()
            };
          }
        }
      }
    });
    
    processMessage();
  });
  
  function processInlineCode(text) {
    if (!text) return text;
    
    // Use marked for basic markdown parsing (excluding code blocks which we handle separately)
    try {
      // Configure marked to not process code blocks
      const tempRenderer = new marked.Renderer();
      tempRenderer.codespan = function(code) {
        const safeCode = typeof code === 'string' ? code : String(code);
        return `<code class="inline-code bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm font-mono">${safeCode}</code>`;
      };
      
      const tempMarked = marked.setOptions({
        breaks: true,
        gfm: true,
        renderer: tempRenderer,
        pedantic: false,
        sanitize: false,
        smartypants: false
      });
      
      // Parse with marked but skip code blocks
      let processedText = marked.parse(text);
      return processedText;
    } catch (error) {
      console.warn('Markdown processing failed, using fallback:', error);
      // Fallback: Handle inline code patterns manually
      return text
        .replace(/`([^`\n]+)`/g, '<code class="inline-code bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm font-mono">$1</code>')
        // Handle cases with special characters in inline code
        .replace(/`([^`]*[-_$@#%&*+=|\\/?<>.,;:!^()[\]{}]+[^`]*)`/g, '<code class="inline-code bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm font-mono">$1</code>')
        // Convert line breaks to HTML
        .replace(/\n/g, '<br>');
    }
  }
  
  function sanitizeContent(content) {
    let safeContent = content;
    
    // Handle different content types properly
    if (typeof content !== 'string') {
      if (content === null || content === undefined) {
        safeContent = '';
      } else if (typeof content === 'object') {
        // Check if the object has meaningful content properties
        if (content.hasOwnProperty('content')) {
          safeContent = String(content.content);
        } else if (content.hasOwnProperty('text')) {
          safeContent = String(content.text);
        } else {
          // Try to stringify, but avoid [object Object]
          try {
            const stringified = JSON.stringify(content);
            if (stringified !== '{}' && stringified !== 'null') {
              safeContent = stringified;
            } else {
              safeContent = '[Invalid content]';
            }
          } catch (e) {
            safeContent = '[Invalid content]';
          }
        }
      } else {
        safeContent = String(content);
      }
    }
    
    // Only remove [object Object] if it's actually meaningless
    if (safeContent === '[object Object]' || safeContent === 'undefined' || safeContent === 'null') {
      safeContent = '';
    }
    
    return safeContent.trim();
  }
  
  function parseContentToBlocks(content) {
    const blocks = [];
    const safeContent = sanitizeContent(content);
    
    if (!safeContent) return blocks;
    
    console.log('Parsing content for code blocks:', safeContent.substring(0, 100));
    
    // Parse code blocks and text separately
    const codeBlockRegex = /```(\w*)\n?([\s\S]*?)```/g;
    let lastIndex = 0;
    let match;
    let codeBlocksFound = 0;
    
    while ((match = codeBlockRegex.exec(safeContent)) !== null) {
      codeBlocksFound++;
      console.log('Found code block:', { lang: match[1], code: match[2].substring(0, 50) });
      
      // Add text before code block
      const textBefore = safeContent.slice(lastIndex, match.index);
      if (textBefore.trim()) {
        // Process text with markdown (but not code blocks)
        const processedText = processInlineCode(textBefore);
        blocks.push({
          type: 'html',
          content: processedText
        });
      }
      
      // Add code block
      const language = match[1] || 'text';
      const code = match[2].trim();
      blocks.push({
        type: 'code',
        content: code,
        language: language
      });
      
      lastIndex = codeBlockRegex.lastIndex;
    }
    
    console.log('Code blocks found:', codeBlocksFound);
    
    // Add remaining text after last code block
    const textAfter = safeContent.slice(lastIndex);
    if (textAfter.trim()) {
      const processedText = processInlineCode(textAfter);
      blocks.push({
        type: 'html',
        content: processedText
      });
    }
    
    // If no code blocks were found, process as regular text
    if (blocks.length === 0 && safeContent.trim()) {
      const processedText = processInlineCode(safeContent);
      blocks.push({
        type: 'html',
        content: processedText
      });
    }
    
    console.log('Final blocks:', blocks.map(b => ({ type: b.type, lang: b.language, content: b.content?.substring(0, 30) })));
    return blocks;
  }
  
  function processMessage() {
    if (!mounted) return;
    
    const content = sanitizeContent(message.content);
    
    if (message.sender === 'bot') {
      // Handle <think> tags for bot messages
      const thinkMatch = content.match(/<think>(.*?)<\/think>/s);
      
      if (thinkMatch) {
        const cleanContent = content.replace(/<think>.*?<\/think>/s, '');
        processedContent = parseContentToBlocks(cleanContent);
        
        processedContent.push({
          type: 'think',
          content: thinkMatch[1].trim()
        });
      } else {
        // Parse all bot content for code blocks and text
        processedContent = parseContentToBlocks(content);
      }
    } else {
      // User messages - simple text
      processedContent = [{
        type: 'text',
        content: content
      }];
    }
  }
  
  $: if (mounted && message) {
    processMessage();
  }
</script>

<div class="flex {message.sender === 'user' ? 'justify-end' : 'justify-start'}">
  <div class="flex space-x-3 max-w-2xl">
    {#if message.sender === 'bot'}
      <div class="flex-shrink-0">
        <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
          <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
      </div>
    {/if}

    <div class="flex flex-col {message.sender === 'user' ? 'items-end' : 'items-start'}">
      <div class="
        {message.sender === 'user' 
          ? 'bg-blue-500 text-white' 
          : 'bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600'
        }
        rounded-2xl px-4 py-3 max-w-full
        {message.isError ? 'border-red-500 bg-red-50 dark:bg-red-900 text-red-600 dark:text-red-200' : ''}
      ">
        {#if message.sender === 'user'}
          <!-- User message content -->
          {#if message.images && message.images.length > 0}
            <div class="mb-2">
              <div class="flex flex-wrap gap-2">
                {#each message.images as image}
                  <div class="relative group">
                    <button
                      type="button"
                      on:click={() => window.open(image.dataUrl, '_blank')}
                      class="block rounded-lg overflow-hidden border border-white/20 hover:border-white/40 transition-colors"
                      aria-label="Open {image.name} in full size"
                    >
                      <img
                        src={image.dataUrl}
                        alt={image.name}
                        class="max-w-48 max-h-48 object-cover"
                      />
                    </button>
                    <div class="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs p-1 rounded-b-lg truncate pointer-events-none">
                      {image.name}
                    </div>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
          
          {#if message.content.trim()}
            <p class="text-sm whitespace-pre-wrap">{message.content}</p>
          {/if}
        {:else}
          {#if message.isComplete}
            <div class="message-content">
              {#each processedContent as block}
                {#if block.type === 'code'}
                  <div class="my-3">
                    <CodeBlock code={block.content} language={block.language} />
                  </div>
                {:else if block.type === 'think'}
                  <details class="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <summary class="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300">Show reasoning...</summary>
                    <div class="mt-2 text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{block.content}</div>
                  </details>
                {:else if block.type === 'html'}
                  <div class="prose prose-sm dark:prose-invert max-w-none">
                    {@html block.content}
                  </div>
                {:else if block.type === 'text'}
                  <p class="text-sm whitespace-pre-wrap">{block.content}</p>
                {/if}
              {/each}
            </div>
          {:else}
            <div class="streaming-content">
              {#each processedContent as block}
                {#if block.type === 'code'}
                  <div class="my-3">
                    <CodeBlock code={block.content} language={block.language} />
                  </div>
                {:else if block.type === 'html'}
                  <div class="text-sm whitespace-pre-wrap">
                    {@html block.content}<span class="animate-pulse">|</span>
                  </div>
                {:else if block.type === 'text'}
                  <p class="text-sm whitespace-pre-wrap">{block.content}<span class="animate-pulse">|</span></p>
                {/if}
              {/each}
            </div>
          {/if}
        {/if}
      </div>

      <div class="text-xs text-gray-600 dark:text-gray-400 mt-1 px-1">
        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </div>
    </div>

    {#if message.sender === 'user'}
      <div class="flex-shrink-0">
        <div class="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
          <svg class="w-4 h-4 text-gray-600 dark:text-gray-300" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .streaming-content {
    transform: translateZ(0);
  }
  
  .message-content {
    contain: layout;
  }
  
  /* Global styles for inline code in markdown */
  :global(.inline-code) {
    background-color: rgba(175, 184, 193, 0.2);
    padding: 0.125rem 0.25rem;
    border-radius: 0.25rem;
    font-family: 'Fira Code', monospace;
    font-size: 0.875em;
  }
  
  :global(.dark .inline-code) {
    background-color: rgba(229, 231, 235, 0.1);
  }
</style>
