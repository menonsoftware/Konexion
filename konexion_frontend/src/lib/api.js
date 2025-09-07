// API service for backend communication
const API_BASE_URL = typeof window !== 'undefined' && import.meta.env.DEV ? '/api' : 'http://localhost:8000/api';

export async function fetchAvailableModels() {
  try {
    const response = await fetch(`${API_BASE_URL}/models`);
    if (!response.ok) {
      throw new Error('Failed to fetch models');
    }
    const data = await response.json();
    return data.models || [];
  } catch (error) {
    console.error('Error fetching models:', error);
    // Return default models if API fails
    return [
      { model_id: 'llama3-8b-8192', context_window: 8192, owned_by: 'meta', client_type: 'groq' },
      { model_id: 'mixtral-8x7b-32768', context_window: 32768, owned_by: 'mistral', client_type: 'groq' },
      { model_id: 'gemma-7b-it', context_window: 8192, owned_by: 'google', client_type: 'groq' }
    ];
  }
}

export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
}
