# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

> **IMPORTANT:** Refer to [AGENTS.md](./AGENTS.md) for the full organizational standards and authentication patterns.

## Context
This repository is part of the **Extended Data Library** ecosystem.

## Development Workflow
```bash
# Check current context
cat memory-bank/activeContext.md 2>/dev/null || echo "No active context"

# Run tests (Python)
[ -f pyproject.toml ] && uv run pytest

# Run tests (Node)
[ -f package.json ] && npm test
```

## Specific Instructions
- Follow Conventional Commits for all PRs.
- Ensure all new features include updated documentation in `docs/`.
- Maintain the `memory-bank/` if present.
