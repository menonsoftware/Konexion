# Pre-commit Configuration for Konexion

This repository uses [pre-commit](https://pre-commit.com/) to ensure code quality and consistency across both the frontend and backend.

## What's Included

### Backend (Python) Checks
- **Ruff**: Modern Python linter and formatter (replaces flake8, black, isort)
- **MyPy**: Static type checking
- **Bandit**: Security vulnerability scanner
- **Import sorting**: Automatic import organization

### Frontend (JavaScript/Svelte) Checks
- **ESLint**: JavaScript/Svelte linting
- **Prettier**: Code formatting for JS, CSS, JSON, Markdown
- **Import validation**: Ensures proper import structure

### General Checks
- **Trailing whitespace removal**
- **End-of-file fixer**
- **YAML/JSON/TOML validation**
- **Large file detection**
- **Merge conflict detection**

## Installation

Pre-commit hooks are automatically installed when you run the setup. If you need to install them manually:

```bash
cd source
pre-commit install
```

## Running Checks Manually

### All Checks
```bash
# Run all pre-commit hooks on all files
pre-commit run --all-files

# Run pre-commit on staged files only
pre-commit run
```

### Backend Specific
```bash
cd konexion_backend

# Run linting
uv run ruff check .

# Fix linting issues automatically
uv run ruff check . --fix

# Format code
uv run ruff format .

# Type checking
uv run mypy .

# Security scan
uv run bandit -r . -c bandit.yaml

# Run all backend checks
uv run python -c "import subprocess; subprocess.run(['ruff', 'check', '.']); subprocess.run(['ruff', 'format', '--check', '.']); subprocess.run(['mypy', '.']); subprocess.run(['bandit', '-r', '.', '-c', 'bandit.yaml'])"
```

### Frontend Specific
```bash
cd konexion_frontend

# Format code
npm run format

# Check formatting without fixing
npm run format:check

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Run all frontend checks
npm run check-all
```

## Configuration Files

- **`.pre-commit-config.yaml`**: Main pre-commit configuration
- **`konexion_backend/ruff.toml`**: Ruff (Python) configuration
- **`bandit.yaml`**: Security scanner configuration
- **`mypy.ini`**: Type checker configuration
- **`.yamllint.yaml`**: YAML linting configuration

## Bypassing Hooks (Use Sparingly)

If you need to commit without running hooks (not recommended):

```bash
git commit --no-verify -m "commit message"
```

## Updating Hooks

To update all hooks to their latest versions:

```bash
pre-commit autoupdate
```

## Troubleshooting

### Hook Installation Issues
If hooks aren't running:
```bash
pre-commit uninstall
pre-commit install
```

### Cache Issues
If you're seeing stale results:
```bash
pre-commit clean
```

### Python Environment Issues
Make sure you're in the correct Python environment:
```bash
cd konexion_backend
source .venv/bin/activate  # or equivalent for your setup
```

## IDE Integration

Most modern IDEs can integrate with these tools:

### VS Code
Install these extensions:
- Ruff (for Python)
- ESLint (for JavaScript/Svelte)
- Prettier (for formatting)
- MyPy Type Checker

### PyCharm/IntelliJ
- Enable Ruff as external tool
- Configure MyPy as type checker
- Enable ESLint for frontend files

## Best Practices

1. **Run checks locally** before committing
2. **Fix issues immediately** rather than accumulating them
3. **Don't bypass hooks** unless absolutely necessary
4. **Keep dependencies updated** regularly
5. **Configure your IDE** to show issues in real-time

## Adding New Hooks

To add new hooks, edit `.pre-commit-config.yaml` and run:
```bash
pre-commit install
pre-commit run --all-files  # Test the new hooks
```
