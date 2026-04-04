/**
 * Auth store and helper functions.
 *
 * user            — current authenticated User object, or null
 * isAuthenticated — derived boolean
 * availableProviders — list of {id, name, icon_hint} from /api/auth/providers
 */

import { derived, writable } from 'svelte/store';
import { goto } from '$app/navigation';
import { config } from './config.js';

const API = config.api.baseUrl;

// ── Stores ────────────────────────────────────────────────────────────────────

export const user = writable(null);
export const isAuthenticated = derived(user, ($user) => $user !== null);
export const availableProviders = writable([]);

// ── API calls ─────────────────────────────────────────────────────────────────

/**
 * Fetch current user from the backend.
 * Sets the user store on success, null on any failure.
 * Returns the user object or null.
 */
export async function checkAuth() {
	try {
		const res = await fetch(`${API}/auth/me`, { credentials: 'include' });
		if (res.ok) {
			const data = await res.json();
			user.set(data);
			return data;
		}
	} catch {
		// Network error — treat as unauthenticated
	}
	user.set(null);
	return null;
}

/**
 * Load the list of enabled OAuth providers from the backend and populate
 * the availableProviders store.  Safe to call multiple times.
 */
export async function loadProviders() {
	try {
		const res = await fetch(`${API}/auth/providers`, { credentials: 'include' });
		if (res.ok) {
			const data = await res.json();
			availableProviders.set(data.providers ?? []);
		}
	} catch {
		// Non-critical — login page will show fallback
	}
}

/**
 * Start the OAuth flow for a given provider.
 * Navigates the browser to the backend login URL which will redirect to the provider.
 */
export function login(provider) {
	window.location.href = `${API}/auth/${provider}/login`;
}

/**
 * Log out: call backend to revoke refresh token, clear user store, redirect to /login.
 */
export async function logout() {
	try {
		await fetch(`${API}/auth/logout`, {
			method: 'POST',
			credentials: 'include'
		});
	} catch {
		// Fire-and-forget — always clear client state
	}
	user.set(null);
	goto('/login');
}

/**
 * Attempt a silent token refresh.
 * Returns true if successful, false otherwise.
 */
export async function silentRefresh() {
	try {
		const res = await fetch(`${API}/auth/refresh`, {
			method: 'POST',
			credentials: 'include'
		});
		if (res.ok) {
			await checkAuth();
			return true;
		}
	} catch {
		// ignore
	}
	user.set(null);
	return false;
}
