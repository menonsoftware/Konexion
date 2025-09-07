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
  export let confirmClass = 'px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 border border-blue-600 rounded-lg transition-colors focus:ring-2 focus:ring-blue-500 focus:border-blue-500';
  export let cancelClass = 'px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 rounded-lg transition-colors focus:ring-2 focus:ring-gray-500 focus:border-gray-500';
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
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[9999]"
    on:click={handleBackdropClick}
  >
    <!-- Modal Content -->
    <div 
      class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6 border border-gray-200 dark:border-gray-600"
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? "modal-title" : undefined}
    >
      <!-- Modal Header -->
      {#if title || icon}
        <div class="flex items-center space-x-3 mb-4">
          {#if icon}
            <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center {icon.bgClass || 'bg-gray-100 dark:bg-gray-700'}">
              {@html icon.svg}
            </div>
          {/if}
          {#if title}
            <div>
              <h3 id="modal-title" class="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
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
          <p class="text-gray-700 dark:text-gray-300">{content}</p>
        </div>
      {/if}

      <!-- Modal Actions -->
      <div class="flex space-x-3 justify-end">
        <button
          type="button"
          on:click={handleCancel}
          class={cancelClass}
        >
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
