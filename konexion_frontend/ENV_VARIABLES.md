# Environment Variables Documentation

This document describes all environment variables used in the Konexion frontend application.

## Setup

1. Copy the example environment file:
   ```bash
   cp example.env .env
   ```

2. Edit the `.env` file according to your environment configuration.

## Environment Variables

### Required Variables

#### `VITE_API_BASE_URL`
- **Description**: Base URL for the backend API server
- **Default**: `http://localhost:8000/api`
- **Example**: `https://api.konexion.com/api`
- **Used in**: API calls for fetching models and health checks

#### `VITE_WS_HOST`
- **Description**: WebSocket host and port for real-time communication
- **Default**: `localhost:8000`
- **Example**: `wss://api.konexion.com`
- **Used in**: WebSocket connections for chat functionality

### Optional Variables

#### `VITE_API_PROXY_PATH`
- **Description**: API proxy path used by Vite dev server
- **Default**: `/api`
- **Example**: `/backend-api`
- **Used in**: Development proxy configuration

#### `VITE_WS_PATH`
- **Description**: WebSocket endpoint path
- **Default**: `/ws/chat`
- **Example**: `/websocket/chat`
- **Used in**: WebSocket URL construction

#### `VITE_DEV_MODE`
- **Description**: Enable development mode features
- **Default**: `true`
- **Example**: `false`
- **Used in**: Development-specific configurations

#### `VITE_DEFAULT_MODELS`
- **Description**: Fallback models when API fails (JSON string)
- **Default**: See example.env for full JSON
- **Example**: `'[{"model_id":"custom-model","context_window":4096}]'`
- **Used in**: Model selection when backend is unavailable

### Performance Variables

#### `VITE_BUFFER_FLUSH_INTERVAL`
- **Description**: Buffer flush interval in milliseconds for streaming
- **Default**: `16` (60fps)
- **Example**: `33` (30fps)
- **Used in**: WebSocket message buffering

#### `VITE_MIN_CHUNK_SIZE`
- **Description**: Minimum chunk size before flushing buffer
- **Default**: `10`
- **Example**: `20`
- **Used in**: WebSocket message buffering optimization

#### `VITE_MAX_RECONNECT_ATTEMPTS`
- **Description**: Maximum WebSocket reconnection attempts
- **Default**: `5`
- **Example**: `10`
- **Used in**: WebSocket connection reliability

### AI Model Configuration

#### `VITE_DEFAULT_MAX_TOKENS`
- **Description**: Default maximum tokens for AI responses
- **Default**: `2048`
- **Example**: `4096`
- **Used in**: Setting initial max tokens value for AI model responses

## Configuration Usage

The application uses a centralized configuration system in `src/lib/config.js`. This file:

1. Loads all environment variables
2. Provides default values for optional variables
3. Validates configuration on startup
4. Exports a structured config object

## Development vs Production

### Development Mode
- Uses proxy configuration for API calls (`/api` → backend server)
- WebSocket connects to `localhost:8000` by default
- Additional debugging and development features enabled

### Production Mode
- Direct API calls to `VITE_API_BASE_URL`
- WebSocket connects to the current host or specified `VITE_WS_HOST`
- Optimized for performance

## Validation

The application includes configuration validation that will:
- Check for required environment variables
- Log warnings for missing optional variables
- Provide fallback values where appropriate

To manually validate configuration:
```javascript
import { validateConfig } from '$lib/config.js';
const isValid = validateConfig();
```

## Security Notes

1. **Never commit `.env` files** - They are included in `.gitignore`
2. **Use `example.env`** as a template for new environments
3. **Prefix all variables with `VITE_`** to make them available in the client
4. **Be careful with sensitive data** - Environment variables are visible in the client bundle
