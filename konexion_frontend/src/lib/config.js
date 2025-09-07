// Frontend configuration utility
// Centralized environment variable handling

export const config = {
  // API Configuration
  api: {
    baseUrl: typeof window !== 'undefined' && import.meta.env.DEV 
      ? (import.meta.env.VITE_API_PROXY_PATH || '/api')
      : (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'),
    proxyPath: import.meta.env.VITE_API_PROXY_PATH || '/api'
  },

  // WebSocket Configuration
  websocket: {
    host: import.meta.env.DEV 
      ? (import.meta.env.VITE_WS_HOST || 'localhost:8000')
      : window?.location?.host || 'localhost:8000',
    path: import.meta.env.VITE_WS_PATH || '/ws/chat',
    maxReconnectAttempts: parseInt(import.meta.env.VITE_MAX_RECONNECT_ATTEMPTS) || 5
  },

  // Performance Configuration
  performance: {
    bufferFlushInterval: parseInt(import.meta.env.VITE_BUFFER_FLUSH_INTERVAL) || 16,
    minChunkSize: parseInt(import.meta.env.VITE_MIN_CHUNK_SIZE) || 10
  },

  // AI Model Configuration
  ai: {
    defaultMaxTokens: parseInt(import.meta.env.VITE_DEFAULT_MAX_TOKENS) || 2048,
    maxTokensOptions: [512, 1024, 2048, 4096, 8192, 16384].map(value => ({
      value,
      label: value.toLocaleString()
    }))
  },

  // Default Models Configuration
  defaultModels: (() => {
    try {
      const defaultModelsJson = import.meta.env.VITE_DEFAULT_MODELS;
      if (defaultModelsJson) {
        return JSON.parse(defaultModelsJson);
      }
    } catch (parseError) {
      console.error('Error parsing default models from environment:', parseError);
    }
    
    // Fallback default models
    return [
      { model_id: 'llama3-8b-8192', context_window: 8192, owned_by: 'meta', client_type: 'groq' },
      { model_id: 'mixtral-8x7b-32768', context_window: 32768, owned_by: 'mistral', client_type: 'groq' },
      { model_id: 'gemma-7b-it', context_window: 8192, owned_by: 'google', client_type: 'groq' }
    ];
  })(),

  // Development Configuration
  isDev: import.meta.env.DEV || import.meta.env.VITE_DEV_MODE === 'true'
};

// Validation function to check if all required environment variables are present
export function validateConfig() {
  const requiredVars = [
    'VITE_API_BASE_URL',
    'VITE_WS_HOST'
  ];
  
  const missing = requiredVars.filter(varName => !import.meta.env[varName]);
  
  if (missing.length > 0) {
    console.warn('Missing environment variables:', missing);
    console.warn('Please check your .env file and ensure all required variables are set.');
  }
  
  return missing.length === 0;
}

// Function to get WebSocket URL
export function getWebSocketUrl() {
  const protocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${config.websocket.host}${config.websocket.path}`;
}
