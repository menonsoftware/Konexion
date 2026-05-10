# Custom AI Agents for Konexion

## Purpose
This file defines custom AI agent modes and skills to assist developers working on the Konexion project. These agents are tailored to the backend, frontend, and DevOps workflows.

## Agent Modes

### Backend Python Agent
- **Focus**: FastAPI patterns, async/ORM, OAuth.
- **Skills**:
  - Generate route handlers with dependency injection.
  - Suggest SQLAlchemy models with `Mapped` fields.
  - Validate JWT token handling.

### Frontend Svelte Agent
- **Focus**: SvelteKit, reactive stores, WebSocket.
- **Skills**:
  - Generate Svelte components with kebab-case filenames.
  - Suggest writable stores for state management.
  - Validate WebSocket configurations.

### DevOps Agent
- **Focus**: Makefile, pre-commit, environment setup.
- **Skills**:
  - Suggest `make` commands for setup and testing.
  - Validate pre-commit hook configurations.
  - Document environment variable usage.

## References
- [GitHub Copilot Instructions](.github/copilot-instructions.md)
- [Backend README](konexion_backend/README.md)
- [Frontend README](konexion_frontend/README.md)