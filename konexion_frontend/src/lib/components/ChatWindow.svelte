<script>
  import { messages, isTyping } from '$lib/stores.js';
  import { onMount, afterUpdate, tick } from 'svelte';
  import MessageBubble from './MessageBubble.svelte';
  import TypingIndicator from './TypingIndicator.svelte';
  import WelcomeMessage from './WelcomeMessage.svelte';

  let chatContainer;
  let showWelcome = true;
  let lastScrollHeight = 0;
  let autoScrollEnabled = true;
  let scrollThrottleTimer = null;

  // Optimized auto-scroll function with throttling
  function scrollToBottom() {
    if (!chatContainer || !autoScrollEnabled) return;
    
    if (scrollThrottleTimer) return; // Skip if already scheduled
    
    scrollThrottleTimer = requestAnimationFrame(() => {
      if (chatContainer) {
        const { scrollTop, scrollHeight, clientHeight } = chatContainer;
        
        // Only scroll if we're near the bottom (within 100px) or if content increased
        const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
        const contentIncreased = scrollHeight > lastScrollHeight;
        
        if (isNearBottom || contentIncreased) {
          chatContainer.scrollTop = scrollHeight;
          lastScrollHeight = scrollHeight;
        }
      }
      scrollThrottleTimer = null;
    });
  }

  // Detect if user has scrolled up manually
  function handleScroll() {
    if (!chatContainer) return;
    
    const { scrollTop, scrollHeight, clientHeight } = chatContainer;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 10;
    
    autoScrollEnabled = isAtBottom;
  }

  // Auto-scroll when new messages arrive or content changes
  afterUpdate(() => {
    scrollToBottom();
  });

  // More efficient reactive statement for messages
  $: if ($messages.length > 0) {
    if (showWelcome) showWelcome = false;
    
    // Use tick() to ensure DOM updates before scrolling
    tick().then(() => {
      scrollToBottom();
    });
  }

  onMount(() => {
    if ($messages.length > 0) {
      showWelcome = false;
    }
    
    // Add passive scroll listener for better performance
    if (chatContainer) {
      chatContainer.addEventListener('scroll', handleScroll, { passive: true });
    }
    
    return () => {
      if (chatContainer) {
        chatContainer.removeEventListener('scroll', handleScroll);
      }
      if (scrollThrottleTimer) {
        cancelAnimationFrame(scrollThrottleTimer);
      }
    };
  });
</script>

<div 
  class="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-4 bg-white dark:bg-gray-800" 
  bind:this={chatContainer}
>
  {#if showWelcome}
    <WelcomeMessage />
  {/if}

  {#each $messages as message (message.id)}
    <div class="fade-in">
      <MessageBubble {message} />
    </div>
  {/each}

  {#if $isTyping}
    <div class="fade-in">
      <TypingIndicator />
    </div>
  {/if}
</div>
