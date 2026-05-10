# GitHub Copilot Instructions

## Purpose
This file provides guidance for GitHub Copilot to assist developers working on the Konexion project. It ensures that Copilot generates code aligned with the project's conventions and architecture.

## Key Conventions

### Backend (Python)
- Use **FastAPI** patterns for route definitions.
- Always use **async/await** for database and API calls.
- Follow **SQLAlchemy 2.x** ORM conventions with `Mapped` fields.
- Use `get_*_config()` helpers for environment variables.
- JWT tokens: Access (15m) + Refresh (7d) stored in HttpOnly cookies.

### Frontend (Svelte)
- Use **Svelte writable stores** for state management.
- Follow **kebab-case** for filenames (e.g., `ChatInput.svelte`).
- Use `VITE_` prefixed environment variables for configuration.
- Avoid exposing secrets in `VITE_` variables.

### General
- Use `make` commands for setup, linting, and testing.
- Follow pre-commit hooks for code quality.
- Documented pitfalls:
  - Backend: SessionMiddleware must precede CORS middleware.
  - Frontend: WebSocket host/port must match `VITE_WS_HOST`.

## References
- [Backend README](konexion_backend/README.md)
- [Frontend README](konexion_frontend/README.md)
- [Environment Variables](konexion_frontend/ENV_VARIABLES.md)
- [Pre-commit Setup](PRE_COMMIT_SETUP.md)