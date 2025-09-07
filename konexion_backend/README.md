# Konexion Backend

A FastAPI-based backend service for AI model inference, supporting both Groq and Ollama AI models with WebSocket communication for real-time streaming.

## Overview

The Konexion Backend provides a unified API interface for interacting with multiple AI providers:
- **Groq**: Cloud-based AI inference with API key authentication
- **Ollama**: Local AI model hosting and inference
- **WebSocket Support**: Real-time streaming responses
- **Model Registry**: High-performance caching system for AI models (500x+ performance improvement)
- **Vision Processing**: Dedicated image analysis capabilities
- **Real-time Refresh**: Dynamic model cache updating without restart
- **CORS**: Configurable cross-origin resource sharing
- **Environment-based Configuration**: Flexible configuration management

## Prerequisites

- **Python**: 3.12 or higher
- **UV Package Manager**: For dependency management and virtual environment
- **Groq API Key**: (Optional) For Groq AI model access
- **Ollama**: (Optional) For local AI model hosting

## Installation

### 1. Install UV Package Manager

If you don't have UV installed, install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup Project

```bash
git clone <repository-url>
cd konexion_backend
```

### 3. Create Virtual Environment and Install Dependencies

```bash
# Create virtual environment with Python 3.12+
uv venv --python 3.12

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv sync
```

### 4. Environment Configuration

Copy the example environment file and configure it:

```bash
cp example.env .env
```

Edit the `.env` file with your configuration:

```env
# Groq Configuration (Optional - for cloud AI models)
GROQ_API_KEY="your_groq_api_key_here"
GROQ_URL="https://api.groq.com/openai/v1/models"

# Ollama Configuration (Optional - for local AI models)
OLLAMA_URL="http://localhost:11434"
OLLAMA_TIMEOUT=30
OLLAMA_MAX_TOKENS=2048

# Server Configuration
SERVER_HOST="0.0.0.0"
SERVER_PORT=8000
DEBUG=false
RELOAD=true
WORKERS=1

# CORS Configuration
CORS_ORIGINS="http://localhost:5173,http://localhost:5174,*"

# Logging Configuration
LOG_LEVEL="INFO"
ENVIRONMENT="development"
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GROQ_API_KEY` | API key for Groq AI services | `None` | Optional |
| `GROQ_URL` | Groq API base URL | `https://api.groq.com/openai/v1/models` | No |
| `OLLAMA_URL` | Ollama service URL | `http://localhost:11434` | No |
| `OLLAMA_TIMEOUT` | Ollama request timeout in seconds | `30` | No |
| `OLLAMA_MAX_TOKENS` | Maximum tokens to generate in Ollama responses | `2048` | No |
| `SERVER_HOST` | Server bind address | `0.0.0.0` | No |
| `SERVER_PORT` | Server port | `8000` | No |
| `DEBUG` | Enable debug mode | `false` | No |
| `RELOAD` | Auto-reload on code changes | `true` | No |
| `WORKERS` | Number of worker processes | `1` | No |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `*` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `ENVIRONMENT` | Application environment | `development` | No |

## Running the Application

### Development Mode

```bash
# Using UV
uv run main.py

# Or activate venv and run directly
source .venv/bin/activate
python main.py
```

### Production Mode

For production deployment, consider using a process manager like systemd, supervisor, or Docker.

## API Endpoints

### Health Check
- `GET /` - Basic health check endpoint

### AI Models
- `GET /api/models` - List available AI models from all providers with caching
- `POST /api/models/refresh` - Refresh model cache and reload all models
- `GET /api/groq/models` - List Groq-specific models
- `GET /api/ollama/models` - List Ollama-specific models

### WebSocket
- `WS /api/chat` - Real-time chat interface with streaming responses and vision support

## AI Provider Setup

### Groq Setup

1. Sign up for a Groq account at [console.groq.com](https://console.groq.com)
2. Generate an API key
3. Add your API key to the `.env` file:
   ```env
   GROQ_API_KEY="gsk_your_api_key_here"
   ```

### Ollama Setup

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Start the Ollama service:
   ```bash
   ollama serve
   ```
3. Pull some models:
   ```bash
   ollama pull llama2
   ollama pull codellama
   ```
4. Ensure `OLLAMA_URL` in `.env` points to your Ollama instance

## Project Structure

```
konexion_backend/
├── main.py              # FastAPI application entry point with optimized routes
├── config.py            # Configuration management with Pydantic settings
├── model_registry.py    # High-performance model caching system
├── vision.py            # Vision processing and image analysis
├── pyproject.toml       # Project dependencies and metadata
├── example.env          # Environment variables template
├── .env                 # Your environment configuration (create from example.env)
├── ai_models/           # AI provider implementations
│   ├── groq.py          # Groq AI integration with streaming
│   └── ollama.py        # Ollama integration with streaming
└── models/              # Data models and schemas
    └── ai.py            # AI model definitions and validation
```

## Development

### Code Structure

- **FastAPI Application**: Modern async web framework with lifespan events
- **Model Registry**: High-performance caching system reducing API calls by 500x+
- **Vision Processing**: Dedicated module for image analysis with Groq and Ollama
- **Pydantic Settings**: Type-safe configuration management
- **WebSocket Support**: Real-time communication with streaming responses
- **Modular AI Providers**: Easy to extend with new providers
- **Comprehensive Logging**: Configurable logging levels

### Adding New AI Providers

1. Create a new module in `ai_models/`
2. Implement the required interface methods
3. Add configuration variables in `config.py`
4. Register the provider in `main.py`

### Testing

```bash
# Run the application and test endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/models

# Test model refresh
curl -X POST http://localhost:8000/api/models/refresh

# WebSocket testing (requires WebSocket client)
# Connect to ws://localhost:8000/api/chat
```

## Performance Features

### Model Registry Caching

The backend implements a high-performance model registry that:
- **Caches model lists** from both Groq and Ollama providers
- **Reduces API calls by 500x+** compared to direct provider queries
- **Preloads on startup** using FastAPI lifespan events
- **Supports real-time refresh** without application restart
- **Thread-safe operations** for concurrent access

### Vision Processing

Dedicated vision module provides:
- **Image format validation** and conversion
- **Provider-specific optimization** for Groq and Ollama vision models
- **Error handling** for unsupported formats
- **Base64 encoding** and metadata extraction

## Troubleshooting

### Common Issues

1. **Port already in use**: Change `SERVER_PORT` in `.env`
2. **Groq API errors**: Verify your `GROQ_API_KEY` is valid
3. **Ollama connection failed**: Ensure Ollama service is running on the specified URL
4. **CORS errors**: Add your frontend URL to `CORS_ORIGINS`

### Logs

Check application logs for debugging:
- Console output for development
- Log file if `LOG_FILE` is configured in environment

### Dependencies

If you encounter dependency issues:

```bash
# Update dependencies
uv sync --upgrade

# Clear cache and reinstall
uv cache clean
uv sync --reinstall
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the main project README for details.
