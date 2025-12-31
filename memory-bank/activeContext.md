# Active Context

## vendor-connectors

Universal vendor connectors for cloud providers and third-party services.

### Included Connectors
- **AWS**: Organizations, SSO, S3, Secrets Manager
- **Google Cloud**: Workspace, Cloud Platform, Billing
- **GitHub**: Repository operations, PR management
- **Slack**: Channel and message operations
- **Vault**: HashiCorp Vault secret management
- **Zoom**: User and meeting management
- **Meshy**: Meshy AI 3D asset generation with AI agent tools

### Package Status
- **Registry**: PyPI
- **Python**: 3.10+ (crewai requires 3.10+)
- **Dependencies**: extended-data-types, lifecyclelogging, directed-inputs-class

### Optional Extras
- `webhooks`: Meshy webhooks support
- `meshy-crewai`: CrewAI tools for Meshy
- `meshy-mcp`: MCP server for Meshy
- `meshy-ai`: All Meshy AI integrations
- `vector`: Vector store for RAG
- `all`: Everything

**Note**: `langchain-core` is a required dependency. We provide TOOLS, you choose your LLM provider.

### Development
```bash
uv sync --extra tests
uv run pytest tests/ -v
```

---

## Meshy AI Tools - NEW ARCHITECTURE

### Status
- **REFACTORED**: AI tools now live with their connectors, not in a central AI package
- **Each connector owns its tools**: `meshy/tools.py`, `meshy/mcp.py`
- **No wrappers**: Use LangChain, CrewAI, and MCP directly

### Structure
```
vendor_connectors/meshy/
├── __init__.py       # API client (existing)
├── tools.py          # LangChain StructuredTools
└── mcp.py            # MCP server
```

### Usage Examples

#### LangChain
```python
from vendor_connectors.meshy.tools import get_tools
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
tools = get_tools()
agent = create_react_agent(llm, tools)

result = agent.invoke({"messages": [("user", "Generate a 3D sword")]})
```

#### CrewAI
```python
from vendor_connectors.meshy.tools import get_crewai_tools
from crewai import Agent

tools = get_crewai_tools()
agent = Agent(role="3D Artist", tools=tools)
```

#### MCP Server
```python
from vendor_connectors.meshy.mcp import create_server, run_server

server = create_server()
run_server(server)

# Or via command line:
# meshy-mcp
```

### Installation
```bash
# Base installation includes langchain-core (required for tools)
pip install vendor-connectors

# CrewAI tools
pip install vendor-connectors[meshy-crewai]

# MCP server
pip install vendor-connectors[meshy-mcp]

# All AI integrations
pip install vendor-connectors[meshy-ai]
```

**Important**: This package provides TOOLS only. You choose and install your LLM provider separately:
```bash
# Choose your LLM provider (not included)
pip install langchain-anthropic  # For Claude
pip install langchain-openai     # For GPT
pip install langchain-google-genai  # For Gemini
# etc.
```

---

## Session: 2025-12-07 (E2E Testing & Documentation)

### Completed
- **VendorConnectorBase created** (`src/vendor_connectors/base.py`)
  - Proper base class for ALL connectors
  - Extends DirectedInputsClass
  - HTTP client with retries, rate limiting
  - MCP/LangChain tool helpers

- **Meshy base.py updated** to use DirectedInputsClass for credential loading

- **ArtStyle enum fixed** per Meshy API docs
  - Changed from invalid values (cartoon, low-poly, sculpt, pbr)
  - To correct values: `realistic`, `sculpture`

- **E2E tests created** (`tests/e2e/meshy/`)
  - `test_langchain.py` - LangGraph ReAct agent tests
  - `test_crewai.py` - CrewAI agent tests
  - `test_strands.py` - AWS Strands agent tests
  - Tests generate REAL 3D models and save GLB files

- **Real artifacts saved**
  - `tests/e2e/fixtures/models/langchain_sword_*.glb` (720KB)
  - VCR cassettes for API replay

- **Documentation created**
  - `AGENTS.md` - Comprehensive agent instructions
  - `.cursor/rules/agents/` - Agent profiles
    - `connector-builder.mdc`
    - `e2e-testing.mdc`
    - `ai-refactor.mdc`
  - Updated `CLAUDE.md` with GITHUB_JBCOM_TOKEN pattern

### Key Patterns Established
1. **GITHUB_JBCOM_TOKEN**: Always use `GH_TOKEN="$GITHUB_JBCOM_TOKEN" gh <command>`
2. **VendorConnectorBase**: All new connectors extend this
3. **Three-Interface Pattern**: API + tools.py + mcp.py
4. **E2E Tests**: Must save real artifacts to prove functionality

### Next Steps
- [ ] Run CrewAI and Strands E2E tests
- [ ] Create sub-issues for other connector AI tooling
- [ ] Update GitHub Projects

---
*Last updated: 2025-12-07*

## Session: 2025-12-24 (AI Tools for All Connectors)

### Completed
- **Refactored all connectors** to inherit from `VendorConnectorBase`:
  - `SlackConnector`, `ZoomConnector`, `VaultConnector`, `GoogleConnector`, `GithubConnector`
- **Updated connector constructors** to use `self.get_input` for transparent credential loading.
- **Implemented AI Tools** for all connectors with Pydantic schemas:
  - `slack/tools.py`: send message, list users, list channels
  - `zoom/tools.py`: list users, create user, remove user
  - `vault/tools.py`: read secret, write secret, list secrets, generate AWS credentials
  - `google/tools.py`: list users, list projects, create project, list folders
  - `github/tools.py`: get file, update file, list org members, list repositories
- **Standardized existing tools** (`aws`, `meshy`) to use Pydantic models for input validation.
- **Updated all __init__.py files** to export `get_tools()`, `get_langchain_tools()`, `get_crewai_tools()`, and `get_strands_tools()`.
- **Verified changes** with `ruff` linting.

### Key Patterns Reinforced
1. **Three-Interface Pattern**: Every connector now provides Python API and AI Framework Tools.
2. **Pydantic Schemas**: All AI tools now use explicit Pydantic models for input validation and schema generation.
3. **VendorConnectorBase**: Now used as the standard base for all connectors in the library.

---
*Last updated: 2025-12-24*
## Session: 2025-12-24
- Updated `directed-inputs-class` dependency to semver constraint `>=0.9.0,<1.0.0` in `pyproject.toml`
- Updated `requires-python` to `>=3.10` and adjusted classifiers to resolve dependency conflicts with `crewai`

---

## Session: 2025-12-29 (Cursor Session Management)

### Overview
Acting as a session manager for Cursor Cloud Agents across multiple repositories.

### Cursor Connector Fixes Applied
- **Agent model**: Made `state` field optional (API returns `status` instead)
- **ConversationMessage model**: Made `role`, `content` fields optional, added `id`, `text`, `type` fields

### Active Sessions Monitored (3 RUNNING)
1. **bc-af73c4b5** - Session management (THIS session) - vendor-connectors
2. **bc-4ea9ae93** - CI fix vignette darkness - arcade-cabinet/otter-elite-force
3. **bc-eaeb7e94** - Sentinel CSP CI fix - arcade-cabinet/protocol-silent-night

### Finished Sessions (17 total)
Notable PRs created by finished agents:
- **otter-elite-force**: PR #72 (vignette adjustment)
- **cosmic-cults**: PR #21 (generator integration)
- **rivermarsh**: PRs #96-104 (boss battles, quests, achievements, mana, mobile polish, persistence)

### Repository Status Summary

| Repository | Open PRs | CI Status | Key Issues |
|------------|----------|-----------|------------|
| otter-elite-force | 7 | PR #66 passing, PR #71 failing | Review feedback pending on PR #66 |
| protocol-silent-night | 9 | Multiple CI failures | CSP blocking workers |
| rivermarsh | 10 | Unknown | Many feature PRs need review |
| cosmic-cults | 8 | Unknown | WIP features in progress |

### Follow-ups Sent
- Sent status check to bc-4ea9ae93 re: PR #66 magic numbers feedback, other PRs needing attention
- Sent status check to bc-eaeb7e94 re: PR #38 CSP fixes, other CI failures

### Next Steps
- [ ] Monitor agent responses to follow-ups
- [ ] Ensure all PRs get proper AI peer review
- [ ] Help agents resolve any blockers
- [ ] Track PRs through to merge

---
*Last updated: 2025-12-29*
## Session: 2025-12-31 (CI Fixes)

### Completed
- **Fixed Ruff formatting issues** across 6 files in `src/` and `tests/`.
- **Resolved Pydantic 2 / CrewAI compatibility issues**:
  - Removed `from __future__ import annotations` from all `tools.py` files (`vault`, `cursor`, `zoom`, `aws`, `google`, `github`, `anthropic`, `slack`, `meshy`).
  - This fixes `pydantic.errors.PydanticUserError: Vault_List_Secrets is not fully defined` when using CrewAI's auto-generation of tools.
- **Verified Vault tool tests** pass locally with `crewai` and `hvac` installed.

### Key Learnings
- `from __future__ import annotations` can cause issues with Pydantic 2 when models are used by external libraries (like CrewAI) that perform runtime introspection and model generation, especially if standard imports like `Optional` are used. Removing it ensures type hints are available as actual types at runtime.

---
