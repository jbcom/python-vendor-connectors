# Extended Data Library - Agentic Instructions

## Overview
The **Extended Data Library** is a collection of high-performance data processing libraries and connectors. This organization uses AI-powered automation for CI/CD, code review, and issue triage.

## CRITICAL: GitHub Authentication
ALWAYS use the `GH_TOKEN` or `GITHUB_TOKEN` provided in the environment. For organization-wide operations, ensure you have the appropriate permissions.

```bash
# Example: List PRs using gh CLI
gh pr list
```

## Development Standards
- **Python**: Use `uv` for dependency management. Follow PEP 8. Use `ruff` for linting and formatting.
- **Node.js**: Use `npm`. Use `eslint` for linting.
- **Documentation**: All repositories must maintain high-quality documentation in the `docs/` directory.

## Architecture Patterns
- **Connectors**: All connectors should extend the base classes provided in `vendor-connectors`.
- **Inputs**: Use the `inputs` library for type-safe configuration.
- **Logging**: Use the `logging` library for standardized output.
- **Automation**: Managed by the [Extended Data Control Center](https://github.com/extended-data-library/control-center).

## AI Orchestration
- **Ecosystem Connector**: Every repository includes an `.github/workflows/ecosystem-connector.yml` that delegates tasks to AI agents.
- **Cursor Rules**: Check `.cursor/rules/` for repo-specific AI instructions. Standardized rules cover PR workflows and fundamentals.
- **Memory Bank**: Use the `memory-bank/` directory to track session context and progress.

## Common Commands
```bash
# Python
uv sync
uv run pytest
uv run ruff check .

# Node.js
npm install
npm test
npm run lint
```

## Documentation Sync
Documentation is built automatically and pushed to `extended-data-library.github.io`. Ensure your `docs/` are up to date.
