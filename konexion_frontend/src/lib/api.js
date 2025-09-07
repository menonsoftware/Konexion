// API service for backend communication
import { config } from './config.js';

const API_BASE_URL = config.api.baseUrl;

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
		return config.defaultModels;
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

export async function refreshModels() {
	try {
		const response = await fetch(`${API_BASE_URL}/models/refresh`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			throw new Error('Failed to refresh models');
		}

		const data = await response.json();

		if (data.status !== 'success') {
			throw new Error(data.message || 'Unknown error occurred');
		}

		return {
			success: true,
			totalModels: data.total_models,
			groqModels: data.groq_models,
			ollamaModels: data.ollama_models,
			message: data.message
		};
	} catch (error) {
		console.error('Error refreshing models:', error);
		return {
			success: false,
			error: error.message
		};
	}
}
