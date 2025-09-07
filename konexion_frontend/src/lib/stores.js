import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { config } from './config.js';

// WebSocket connection store
export const wsConnection = writable(null);

// Chat messages store with performance optimizations
function createMessagesStore() {
  const { subscribe, set, update } = writable([]);
  
  return {
    subscribe,
    set,
    update,
    // Optimized method to update just the last message (for streaming)
    updateLastMessage: (updater) => {
      update(msgs => {
        if (msgs.length === 0) return msgs;
        
        const lastIndex = msgs.length - 1;
        const updatedMsg = updater(msgs[lastIndex]);
        
        // Only create new array if message actually changed
        if (updatedMsg === msgs[lastIndex]) return msgs;
        
        const newMsgs = [...msgs];
        newMsgs[lastIndex] = updatedMsg;
        return newMsgs;
      });
    },
    // Method to add a new message efficiently
    addMessage: (message) => {
      update(msgs => [...msgs, message]);
    },
    // Method to clear all messages
    clear: () => {
      set([]);
    }
  };
}

export const messages = createMessagesStore();

// Available AI models store
export const availableModels = writable([]);

// Selected AI model store
export const selectedModel = writable('');

// Max tokens configuration store with persistence
function createMaxTokensStore() {
  const { subscribe, set, update } = writable(config.ai.defaultMaxTokens);

  return {
    subscribe,
    set: (value) => {
      if (browser) {
        localStorage.setItem('maxTokens', value.toString());
      }
      set(value);
    },
    update,
    init: () => {
      if (browser) {
        const stored = localStorage.getItem('maxTokens');
        if (stored) {
          const parsedValue = parseInt(stored);
          if (!isNaN(parsedValue) && parsedValue > 0) {
            set(parsedValue);
          }
        }
      }
    }
  };
}

export const maxTokens = createMaxTokensStore();

// Connection status store
export const isConnected = writable(false);

// Loading state store
export const isLoading = writable(false);

// Dark mode store
function createDarkModeStore() {
  const { subscribe, set, update } = writable(false);

  let initialized = false;

  return {
    subscribe,
    set,
    update,
    toggle: () => {
      update(dark => {
        const newDark = !dark;
        
        if (browser) {
          // Update localStorage
          localStorage.setItem('theme', newDark ? 'dark' : 'light');
          
          // Update DOM immediately
          if (document?.documentElement) {
            if (newDark) {
              document.documentElement.classList.add('dark');
            } else {
              document.documentElement.classList.remove('dark');
            }
          }
        }
        return newDark;
      });
    },
    init: () => {
      if (browser && !initialized) {
        const stored = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Respect explicit user choice, otherwise use system preference
        const shouldUseDark = stored === 'dark' || (stored === null && prefersDark);
        
        // Apply to DOM immediately (might already be applied by FOUC prevention script)
        if (document?.documentElement) {
          if (shouldUseDark) {
            document.documentElement.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
          }
        }
        
        set(shouldUseDark);
        initialized = true;
      }
    }
  };
}

export const isDarkMode = createDarkModeStore();

// Typing indicator store
export const isTyping = writable(false);

// Global modal store for app-level modals
function createModalStore() {
  const { subscribe, set } = writable({
    show: false,
    title: '',
    description: '',
    content: '',
    confirmText: 'Confirm',
    cancelText: 'Cancel',
    confirmClass: 'px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 border border-blue-600 rounded-lg transition-colors focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
    cancelClass: 'px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 rounded-lg transition-colors focus:ring-2 focus:ring-gray-500 focus:border-gray-500',
    icon: null,
    onConfirm: null,
    onCancel: null
  });

  return {
    subscribe,
    show: (config) => {
      set({
        show: true,
        title: config.title || '',
        description: config.description || '',
        content: config.content || '',
        confirmText: config.confirmText || 'Confirm',
        cancelText: config.cancelText || 'Cancel',
        confirmClass: config.confirmClass || 'px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 border border-blue-600 rounded-lg transition-colors focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
        cancelClass: config.cancelClass || 'px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 rounded-lg transition-colors focus:ring-2 focus:ring-gray-500 focus:border-gray-500',
        icon: config.icon || null,
        onConfirm: config.onConfirm || null,
        onCancel: config.onCancel || null
      });
    },
    hide: () => {
      set({
        show: false,
        title: '',
        description: '',
        content: '',
        confirmText: 'Confirm',
        cancelText: 'Cancel',
        confirmClass: 'px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 border border-blue-600 rounded-lg transition-colors focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
        cancelClass: 'px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 rounded-lg transition-colors focus:ring-2 focus:ring-gray-500 focus:border-gray-500',
        icon: null,
        onConfirm: null,
        onCancel: null
      });
    }
  };
}

export const globalModal = createModalStore();
