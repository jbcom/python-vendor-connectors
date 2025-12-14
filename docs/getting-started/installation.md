# Installation

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Install from PyPI

```bash
# Using uv (recommended)
uv add vendor-connectors

# Using pip
pip install vendor-connectors
```

## Install with Extras

vendor-connectors uses optional dependencies for different vendors and AI frameworks:

```bash
# Install with specific vendors
pip install vendor-connectors[aws]
pip install vendor-connectors[github,slack]

# Install with AI framework support
pip install vendor-connectors[langchain]
pip install vendor-connectors[crewai]

# Install everything
pip install vendor-connectors[all]
```

### Available Extras

**Vendors:**
- `aws` - AWS (boto3)
- `google` - Google Cloud
- `github` - GitHub API
- `slack` - Slack API
- `vault` - HashiCorp Vault
- `meshy` - Meshy 3D AI

**AI Frameworks:**
- `langchain` - LangChain tools
- `crewai` - CrewAI tools
- `strands` - AWS Strands agents
- `mcp` - Model Context Protocol

**Development:**
- `dev` - Development tools (pytest, ruff, mypy)
- `docs` - Documentation (sphinx)
- `tests` - Test dependencies

## Install from Source

```bash
git clone https://github.com/jbcom/vendor-connectors.git
cd vendor-connectors
uv sync
```

## Development Installation

```bash
# Clone and install with all dev dependencies
git clone https://github.com/jbcom/vendor-connectors.git
cd vendor-connectors
uv sync --all-extras
```
