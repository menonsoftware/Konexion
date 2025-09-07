# Konexion

A modern web application for AI model inference and chat interactions, providing a unified interface for both cloud-based and local AI models.

## Overview

Konexion is a full-stack web application that enables seamless interaction with multiple AI providers through an intuitive chat interface. The project consists of two main components:

- **Backend (FastAPI)**: Provides API endpoints and WebSocket connections for AI model inference
- **Frontend (SvelteKit)**: Modern, responsive web interface for chat interactions

## Features

### 🤖 Multi-Provider AI Support
- **Groq**: Cloud-based AI inference with high-performance models
- **Ollama**: Local AI model hosting and inference
- Support for multiple models simultaneously

### 💬 Real-time Chat Interface
- WebSocket-based streaming responses
- Modern, responsive UI built with SvelteKit and Tailwind CSS
- Dark/light mode support
- Keyboard shortcuts for improved productivity

### 🔧 Developer-Friendly
- Type-safe configuration management
- Environment-based setup
- Comprehensive error handling
- Hot-reload development mode

### 🚀 Production-Ready
- CORS configuration for secure deployments
- Configurable logging
- Docker support (optional)
- Scalable architecture

## Architecture

```
┌─────────────────┐    WebSocket/HTTP   ┌─────────────────┐
│                 │ ◄─────────────────► │                 │
│  SvelteKit      │                     │  FastAPI        │
│  Frontend       │                     │  Backend        │
│                 │                     │                 │
└─────────────────┘                     └─────────────────┘
                                                │
                                                │ HTTP/API
                                                ▼
                                        ┌─────────────────┐
                                        │   AI Providers  │
                                        │                 │
                                        │ ┌─────┐ ┌──────┐│
                                        │ │Groq │ │Ollama││
                                        │ └─────┘ └──────┘│
                                        └─────────────────┘
```

## Quick Start

### Prerequisites
- **Node.js**: 18+ (for frontend)
- **Python**: 3.12+ (for backend)
- **UV**: Python package manager
- **pnpm/npm**: Node.js package manager

### 1. Clone the Repository
```bash
git clone <repository-url>
cd source
```

### 2. Backend Setup
```bash
cd konexion_backend

# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv --python 3.12
source .venv/bin/activate
uv sync

# Configure environment
cp example.env .env
# Edit .env with your configuration

# Start the backend
uv run main.py
```

### 3. Frontend Setup
```bash
cd ../konexion_frontend

# Install dependencies
npm install
# or
pnpm install

# Start development server
npm run dev
# or
pnpm dev
```

### 4. Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
source/
├── konexion_backend/          # FastAPI backend application
│   ├── main.py               # Application entry point
│   ├── config.py             # Configuration management
│   ├── pyproject.toml        # Python dependencies
│   ├── ai_models/            # AI provider implementations
│   │   ├── groq.py          # Groq integration
│   │   └── ollama.py        # Ollama integration
│   └── models/              # Data models and schemas
│
├── konexion_frontend/         # SvelteKit frontend application
│   ├── src/
│   │   ├── routes/          # SvelteKit routes
│   │   ├── lib/             # Shared components and utilities
│   │   │   ├── components/  # Svelte components
│   │   │   ├── api.js       # API client
│   │   │   ├── websocket.js # WebSocket management
│   │   │   └── stores.js    # Svelte stores
│   │   └── app.html         # HTML template
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite configuration
│
└── README.md                # This file
```

## Configuration

### Backend Configuration
The backend uses environment variables for configuration. See `konexion_backend/example.env` for all available options:

- **AI Provider Keys**: Configure API keys for Groq and URLs for Ollama
- **Server Settings**: Host, port, CORS origins
- **Development**: Debug mode, auto-reload, logging levels

### Frontend Configuration
The frontend automatically connects to the backend API. Configuration can be adjusted in:
- `vite.config.js`: Vite and build settings
- `svelte.config.js`: SvelteKit configuration
- `tailwind.config.js`: Tailwind CSS customization

## Development

### Backend Development
```bash
cd konexion_backend

# Activate virtual environment
source .venv/bin/activate

# Run with auto-reload
uv run main.py

# Run tests (if available)
# uv run pytest
```

### Frontend Development
```bash
cd konexion_frontend

# Start development server with hot-reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint and format
npm run lint
npm run format
```

### Adding New AI Providers
1. Create a new module in `konexion_backend/ai_models/`
2. Implement the required interface methods
3. Add configuration variables in `config.py`
4. Register the provider in `main.py`
5. Update frontend to handle the new provider

## Deployment

### Production Build
```bash
# Backend
cd konexion_backend
uv sync --no-dev

# Frontend
cd konexion_frontend
npm run build
```

### Environment Variables
Ensure all required environment variables are set in production:
- AI provider API keys
- Server configuration
- CORS origins for your domain

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow Python PEP 8 for backend code
- Use Prettier for frontend code formatting
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

## Troubleshooting

### Common Issues
1. **Backend not starting**: Check Python version and environment variables
2. **Frontend connection errors**: Ensure backend is running on correct port
3. **AI model errors**: Verify API keys and service URLs
4. **CORS errors**: Add frontend URL to backend CORS origins

### Getting Help
- Check the individual README files in each component folder
- Review the API documentation at `/docs` endpoint
- Check application logs for error details

## Roadmap

- [ ] Image and attachment support - WIP
- [ ] User authentication and sessions
- [ ] Chat history persistence
- [ ] Multi-user support
- [ ] Docker containerization
- [ ] Additional AI provider integrations

## License

MIT License

Copyright (c) 2025 Konexion Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
