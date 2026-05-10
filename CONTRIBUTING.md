# Contributing to Konexion

## Pull Request Workflow
1. **Branch Naming**: Use `feature/`, `bugfix/`, or `hotfix/` prefixes.
2. **Testing**: Ensure all tests pass locally.
3. **Pre-commit Hooks**: Run `make pre-commit` before pushing.
4. **Code Review**: Assign at least one reviewer.

## Development Setup
- Install dependencies: `make install-all`
- Start development servers: `make start-all`

## Testing
- Backend: `make test-backend`
- Frontend: `make test-frontend`

## References
- [Pre-commit Setup](PRE_COMMIT_SETUP.md)
- [Environment Variables](konexion_frontend/ENV_VARIABLES.md)