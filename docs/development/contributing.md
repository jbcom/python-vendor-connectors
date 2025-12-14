# Contributing

Thank you for your interest in contributing to vendor-connectors!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/jbcom/vendor-connectors.git
cd vendor-connectors

# Install with all development dependencies
uv sync --all-extras
```

## Running Tests

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=vendor_connectors

# Run a specific test file
uv run pytest tests/test_aws_connector.py -v
```

## Code Style

This project uses:
- [Ruff](https://docs.astral.sh/ruff/) for linting and formatting
- Type hints throughout
- 120 character line length

```bash
# Check code style
uvx ruff check src/ tests/
uvx ruff format --check src/ tests/

# Auto-fix issues
uvx ruff check --fix src/ tests/
uvx ruff format src/ tests/
```

## Building Documentation

```bash
# Install docs dependencies
uv sync --extra docs

# Build docs
cd docs
uv run sphinx-build -b html . _build/html

# Or use make
make html
```

## Project Structure

```
vendor-connectors/
├── src/vendor_connectors/
│   ├── aws/              # AWS connector + tools
│   ├── github/           # GitHub connector
│   ├── google/           # Google Cloud connector
│   ├── slack/            # Slack connector
│   ├── vault/            # HashiCorp Vault
│   ├── zoom/             # Zoom connector
│   ├── meshy/            # Meshy 3D AI + tools
│   ├── anthropic/        # Anthropic Claude
│   ├── cursor/           # Cursor AI agents
│   ├── base.py           # VendorConnectorBase
│   └── connectors.py     # VendorConnectors facade
├── tests/
├── docs/
└── pyproject.toml
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Ensure CI passes (lint + tests)
4. Submit PR - an AI agent will review and merge

## Commit Messages

Use conventional commits:
- `feat(connector):` New features
- `fix(connector):` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

Examples:
```
feat(aws): Add S3 lifecycle management tools
fix(github): Handle rate limiting in list_repositories
docs: Update quickstart with CrewAI example
```

## Adding AI Tools

See [Building Connector Tools](building-connector-tools.md) for a detailed guide on adding AI-callable tools to connectors.
