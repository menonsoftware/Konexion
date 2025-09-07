import { 
  wsConnection, 
  messages, 
  isConnected, 
  isLoading, 
  selectedModel,
  isTyping 
} from '$lib/stores.js';
import { get } from 'svelte/store';
import { browser } from '$app/environment';
import { perfMonitor } from '$lib/performance.js';

let currentBotMessage = null;
let chunkBuffer = '';
let bufferTimeout = null;
const BUFFER_FLUSH_INTERVAL = 16; // 60fps (16ms)
const MIN_CHUNK_SIZE = 10; // Minimum characters before flushing

export class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    if (!browser) return; // Only run on client side
    
    try {
      // Use the backend WebSocket endpoint
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = import.meta.env.DEV ? 'localhost:8000' : window.location.host;
      this.ws = new WebSocket(`${protocol}//${wsHost}/ws/chat`);
      
      wsConnection.set(this.ws);

      this.ws.onopen = () => {
        console.log('WebSocket connection established');
        isConnected.set(true);
        this.reconnectAttempts = 0;
      };

      this.ws.onclose = () => {
        console.log('WebSocket connection closed');
        isConnected.set(false);
        this.handleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        isConnected.set(false);
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event);
        
        // Force immediate reactivity by triggering a microtask
        Promise.resolve().then(() => {
          // This ensures the UI updates immediately after message processing
        });
      };

    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
      isConnected.set(false);
    }
  }

  handleMessage(event) {
    try {
      const data = JSON.parse(event.data);
      
      if (data.error) {
        this.addMessage(data.error, 'bot', true);
        isTyping.set(false);
        isLoading.set(false);
        return;
      }

      if (data.chunk !== undefined && data.chunk !== null) {
        // Handle streaming chunk - ensure it's a string
        let chunk = data.chunk;
        if (typeof chunk !== 'string') {
          chunk = String(chunk);
        }
        this.handleStreamingChunk(chunk);
      } else if (data.finish_reason) {
        this.handleStreamingComplete(data.finish_reason);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
      isLoading.set(false);
      isTyping.set(false);
    }
  }

  handleStreamingChunk(chunk) {
    const startTime = performance.now();
    
    // Properly handle different chunk types
    let cleanChunk = '';
    
    if (typeof chunk === 'string') {
      cleanChunk = chunk;
    } else if (chunk !== null && chunk !== undefined) {
      // Handle objects or other data types properly
      if (typeof chunk === 'object' && chunk.hasOwnProperty('content')) {
        cleanChunk = String(chunk.content);
      } else if (typeof chunk === 'object' && chunk.hasOwnProperty('text')) {
        cleanChunk = String(chunk.text);
      } else {
        // Convert to string but only if it's meaningful content
        const stringified = String(chunk);
        if (stringified !== '[object Object]' && stringified !== 'undefined' && stringified !== 'null') {
          cleanChunk = stringified;
        } else {
          console.warn('Received unexpected chunk format:', chunk);
          return; // Skip malformed chunks
        }
      }
    }
    
    // Skip empty chunks
    if (!cleanChunk) return;

    // Add to buffer instead of immediately updating
    chunkBuffer += cleanChunk;

    if (!currentBotMessage) {
      currentBotMessage = {
        id: Date.now(),
        content: '',
        sender: 'bot',
        timestamp: new Date(),
        isComplete: false
      };
      messages.update(msgs => [...msgs, currentBotMessage]);
    }

    // Clear existing timeout
    if (bufferTimeout) {
      clearTimeout(bufferTimeout);
    }

    // Flush buffer if it's large enough or after a timeout
    if (chunkBuffer.length >= MIN_CHUNK_SIZE) {
      this.flushChunkBuffer();
    } else {
      // Set timeout to flush buffer even for small chunks
      bufferTimeout = setTimeout(() => this.flushChunkBuffer(), BUFFER_FLUSH_INTERVAL);
    }

    // Record performance metrics
    const endTime = performance.now();
    perfMonitor.recordChunk(cleanChunk.length, endTime - startTime);
  }

  flushChunkBuffer() {
    if (!chunkBuffer || !currentBotMessage) return;

    const startTime = performance.now();
    
    // Update message content with buffered chunks
    currentBotMessage.content += chunkBuffer;
    chunkBuffer = '';

    // Use more efficient update that doesn't recreate the entire array
    messages.update(msgs => {
      const lastIndex = msgs.length - 1;
      if (lastIndex >= 0 && msgs[lastIndex].id === currentBotMessage.id) {
        // Create new reference only for the last message to trigger reactivity
        const newMsgs = [...msgs];
        newMsgs[lastIndex] = { ...currentBotMessage };
        return newMsgs;
      }
      return msgs;
    });

    // Clear timeout
    if (bufferTimeout) {
      clearTimeout(bufferTimeout);
      bufferTimeout = null;
    }

    // Record UI update performance
    const endTime = performance.now();
    perfMonitor.recordUIUpdate(endTime - startTime);
  }

  handleStreamingComplete(finishReason) {
    // Flush any remaining buffer before completing
    if (chunkBuffer) {
      this.flushChunkBuffer();
    }

    if (currentBotMessage) {
      currentBotMessage.isComplete = true;
      messages.update(msgs => {
        const lastIndex = msgs.length - 1;
        if (lastIndex >= 0 && msgs[lastIndex].id === currentBotMessage.id) {
          const newMsgs = [...msgs];
          newMsgs[lastIndex] = { ...currentBotMessage };
          return newMsgs;
        }
        return msgs;
      });
      currentBotMessage = null;
    }
    
    // Reset buffer state
    chunkBuffer = '';
    if (bufferTimeout) {
      clearTimeout(bufferTimeout);
      bufferTimeout = null;
    }
    
    isTyping.set(false);
    isLoading.set(false);
  }

  sendMessage(message, model) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      // Clean up the message content before sending
      let cleanMessage = message;
      if (typeof message !== 'string') {
        cleanMessage = String(message);
      }
      cleanMessage = cleanMessage.replace(/\[object Object\]/g, '').trim();
      
      // Add user message to chat
      this.addMessage(cleanMessage, 'user');
      
      // Show loading state
      isLoading.set(true);
      isTyping.set(true);
      
      // Send to backend
      this.ws.send(JSON.stringify({
        message: cleanMessage,
        model: model
      }));
    } else {
      console.error('WebSocket is not connected');
      this.addMessage('Connection error. Please try again.', 'bot', true);
    }
  }

  addMessage(content, sender, isError = false) {
    // Clean up content properly without removing valid content
    let cleanContent = content;
    
    if (typeof content !== 'string') {
      if (content === null || content === undefined) {
        cleanContent = '';
      } else if (typeof content === 'object') {
        // Check for meaningful object properties first
        if (content.hasOwnProperty('content')) {
          cleanContent = String(content.content);
        } else if (content.hasOwnProperty('text')) {
          cleanContent = String(content.text);
        } else {
          try {
            const stringified = JSON.stringify(content);
            if (stringified !== '{}' && stringified !== 'null') {
              cleanContent = stringified;
            } else {
              cleanContent = '[Invalid content]';
            }
          } catch (e) {
            cleanContent = '[Invalid content]';
          }
        }
      } else {
        cleanContent = String(content);
      }
    }
    
    // Only remove if it's actually meaningless [object Object]
    if (cleanContent === '[object Object]' || cleanContent === 'undefined' || cleanContent === 'null') {
      cleanContent = isError ? 'Unknown error occurred' : '';
    }
    
    cleanContent = cleanContent.trim();
    
    const newMessage = {
      id: Date.now() + Math.random(),
      content: cleanContent,
      sender: sender,
      timestamp: new Date(),
      isComplete: true,
      isError: isError
    };
    
    messages.update(msgs => [...msgs, newMessage]);
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      setTimeout(() => this.connect(), 2000 * this.reconnectAttempts);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

export const wsService = new WebSocketService();

// Make available globally for testing in development
if (typeof window !== 'undefined' && import.meta.env.DEV) {
  window.wsService = wsService;
}
