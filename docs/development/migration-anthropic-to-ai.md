# Migration Guide: Anthropic Connector to AI Sub-Package

This guide helps you migrate from the legacy `vendor_connectors.anthropic` connector to the new unified `vendor_connectors.ai` sub-package.

## Overview

The `vendor_connectors.anthropic` connector provides direct access to the Anthropic Claude API with a simple HTTP client wrapper. The new `vendor_connectors.ai` sub-package offers a unified interface across multiple AI providers (Anthropic, OpenAI, Google, xAI, Ollama) with additional features like:

- **Tool Integration**: Auto-generate LangChain tools from vendor connectors
- **Multi-Provider Support**: Switch between providers without code changes
- **Workflow Building**: Create LangGraph workflows with the WorkflowBuilder DSL
- **Observability**: Optional LangSmith tracing for debugging
- **Agent Patterns**: Built-in ReAct agent support with tool calling

## When to Use Which Package

### Use `vendor_connectors.anthropic` When:
- You only need Anthropic Claude API access
- You want minimal dependencies (just httpx)
- You need fine-grained control over API requests
- You're building a simple chat interface

### Use `vendor_connectors.ai` When:
- You want to switch between AI providers
- You need tool calling with vendor connectors
- You're building multi-step workflows with LangGraph
- You want automatic tool generation from connector methods
- You need observability with LangSmith

## Installation

### Anthropic Connector (Existing)
```bash
pip install vendor-connectors
```

### AI Sub-Package (New)
```bash
# Core AI package (includes LangChain/LangGraph)
pip install vendor-connectors[ai]

# With Anthropic provider
pip install vendor-connectors[ai-anthropic]

# All AI providers
pip install vendor-connectors[ai-all]
```

## Migration Examples

### Example 1: Basic Chat

**Before (anthropic connector):**
```python
from vendor_connectors.anthropic import AnthropicConnector

claude = AnthropicConnector(api_key="sk-ant-...")
response = claude.create_message(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)
print(response.text)
```

**After (AI sub-package):**
```python
from vendor_connectors.ai import AIConnector

ai = AIConnector(
    provider="anthropic",
    api_key="sk-ant-...",
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024
)
response = ai.chat("Explain quantum computing")
print(response.content)
```

**Key Differences:**
- `AIConnector` uses a unified `chat()` method instead of `create_message()`
- Response is `AIResponse` object with `.content` instead of `Message` with `.text`
- Temperature and max_tokens are set during initialization, not per-request

### Example 2: Conversation History

**Before:**
```python
messages = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."},
    {"role": "user", "content": "Give me an example"}
]

response = claude.create_message(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=messages
)
```

**After:**
```python
from vendor_connectors.ai.base import AIMessage, MessageRole

history = [
    AIMessage(role=MessageRole.USER, content="What is Python?"),
    AIMessage(role=MessageRole.ASSISTANT, content="Python is a programming language..."),
]

response = ai.chat("Give me an example", history=history)
```

**Key Differences:**
- History uses `AIMessage` objects instead of dicts
- Last message is passed separately to `chat()` method

### Example 3: System Prompts

**Before:**
```python
response = claude.create_message(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    system="You are a helpful coding assistant",
    messages=[{"role": "user", "content": "Write a Python function"}]
)
```

**After:**
```python
response = ai.chat(
    "Write a Python function",
    system_prompt="You are a helpful coding assistant"
)
```

**Key Differences:**
- Parameter name changed from `system` to `system_prompt`

### Example 4: Token Counting

**Before:**
```python
token_count = claude.count_tokens(
    model="claude-sonnet-4-5-20250929",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(f"Tokens: {token_count}")
```

**After:**
```python
# Use the underlying provider directly for token counting
from vendor_connectors.anthropic import AnthropicConnector

# AI sub-package focuses on inference, not token counting
# For token counting, continue using the anthropic connector
claude = AnthropicConnector()
token_count = claude.count_tokens(
    model="claude-sonnet-4-5-20250929",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**Note:** Token counting is not yet available in the AI sub-package. Use the anthropic connector for this feature.

### Example 5: Tool Calling (NEW in AI Sub-Package)

The AI sub-package's main advantage is automatic tool integration:

```python
from vendor_connectors.ai import AIConnector, ToolCategory
from vendor_connectors.github import GithubConnector

# Initialize AI with tools
ai = AIConnector(provider="anthropic")
github = GithubConnector()

# Register GitHub connector methods as tools
ai.register_connector_tools(github, ToolCategory.GITHUB)

# AI can now call GitHub tools automatically
response = ai.invoke(
    "List all repositories in my organization and create an issue for the first one",
    use_tools=True
)
print(response.content)
```

This feature has no equivalent in the anthropic connector.

### Example 6: Multi-Provider Support (NEW)

Switch providers without changing your code:

```python
# Use Anthropic
ai = AIConnector(provider="anthropic", model="claude-sonnet-4-5-20250929")
response = ai.chat("Hello!")

# Switch to OpenAI
ai = AIConnector(provider="openai", model="gpt-4o")
response = ai.chat("Hello!")

# Switch to local Ollama
ai = AIConnector(provider="ollama", model="llama3.2")
response = ai.chat("Hello!")
```

## API Compatibility Matrix

| Feature | Anthropic Connector | AI Sub-Package |
|---------|-------------------|----------------|
| Basic chat | ✅ `create_message()` | ✅ `chat()` |
| System prompts | ✅ `system` param | ✅ `system_prompt` param |
| Conversation history | ✅ Via messages list | ✅ Via `history` param |
| Token counting | ✅ `count_tokens()` | ❌ Use anthropic connector (not planned) |
| Model listing | ✅ `list_models()` | ❌ Use anthropic connector (not planned) |
| Model info | ✅ `get_model()` | ❌ Use anthropic connector (not planned) |
| Agent execution | ✅ `execute_agent_task()` | ✅ `invoke()` with tools |
| Tool calling | ❌ Manual | ✅ Auto-generated from connectors |
| Multi-provider | ❌ Anthropic only | ✅ 5+ providers |
| Workflows | ❌ | ✅ WorkflowBuilder DSL |
| Observability | ❌ | ✅ LangSmith integration |

## Response Object Comparison

### AnthropicConnector Response (Message)
```python
response.id               # Message ID
response.type             # "message"
response.role             # MessageRole.ASSISTANT
response.content          # List[ContentBlock]
response.text             # Convenience property for text content
response.model            # Model used
response.stop_reason      # Why generation stopped
response.usage.input_tokens   # Input token count
response.usage.output_tokens  # Output token count
```

### AIConnector Response (AIResponse)
```python
response.content          # Text content (string)
response.model            # Model used
response.provider         # AIProvider enum
response.usage            # Dict with input_tokens, output_tokens
response.tool_calls       # List of tool calls if any
response.stop_reason      # Why generation stopped
response.raw_response     # Original LangChain response
```

## Environment Variables

Both packages use the same environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

The AI sub-package also supports:
```bash
export LANGCHAIN_TRACING_V2="true"        # Enable LangSmith tracing
export LANGCHAIN_API_KEY="lsv2_..."       # LangSmith API key
export LANGCHAIN_PROJECT="my-project"     # LangSmith project name
```

## Code-Level Initialization

### AnthropicConnector
```python
connector = AnthropicConnector(
    api_key="sk-ant-...",           # API key
    api_version="2023-06-01",       # API version
    timeout=60.0,                   # Request timeout
)
```

### AIConnector (Anthropic Provider)
```python
ai = AIConnector(
    provider="anthropic",           # Provider name
    model="claude-sonnet-4-5-20250929",  # Model
    api_key="sk-ant-...",           # API key
    temperature=0.7,                # Sampling temperature
    max_tokens=4096,                # Max output tokens
    langsmith_api_key="lsv2_...",   # Optional LangSmith
)
```

## Exception Handling

### AnthropicConnector
```python
from vendor_connectors.anthropic import (
    AnthropicError,
    AnthropicAuthError,
    AnthropicRateLimitError,
    AnthropicAPIError
)

try:
    response = claude.create_message(...)
except AnthropicAuthError as e:
    print(f"Auth failed: {e.message}")
except AnthropicRateLimitError as e:
    print(f"Rate limited: {e.message}")
except AnthropicAPIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
```

### AIConnector
```python
# AI sub-package uses LangChain exceptions
try:
    response = ai.chat("...")
except ImportError as e:
    print("LangChain not installed")
except Exception as e:
    # Catch LangChain-specific exceptions
    print(f"Error: {e}")
```

## Gradual Migration Strategy

You don't have to migrate all at once. Both packages can coexist:

```python
from vendor_connectors.anthropic import AnthropicConnector
from vendor_connectors.ai import AIConnector, ToolCategory
from vendor_connectors.github import GithubConnector

# Use anthropic connector for token counting
claude = AnthropicConnector()
token_count = claude.count_tokens(
    model="claude-sonnet-4-5-20250929",
    messages=[{"role": "user", "content": "Hello"}]
)

# Use AI sub-package for tool calling
# Note: Connectors read credentials from environment variables (GITHUB_TOKEN, etc.)
ai = AIConnector(provider="anthropic")
github = GithubConnector()  # Reads GITHUB_TOKEN from environment
ai.register_connector_tools(github, ToolCategory.GITHUB)
response = ai.invoke("List my repos", use_tools=True)
```

## Best Practices

### For Simple Chat Applications
Stay with `vendor_connectors.anthropic` unless you need:
- Tool calling with vendor connectors
- Multi-provider support
- Workflow orchestration

### For Agent Applications
Migrate to `vendor_connectors.ai` to leverage:
- Automatic tool generation from connectors
- ReAct agent pattern with `invoke()`
- LangGraph workflow integration

### For Production Systems
Consider:
- **Observability**: Use LangSmith integration in AI sub-package
- **Token Costs**: Use anthropic connector's `count_tokens()` for budgeting
- **Flexibility**: Start with AI sub-package to enable future provider switches

## Getting Help

- **Anthropic Connector Docs**: See `src/vendor_connectors/anthropic/__init__.py`
- **AI Sub-Package Docs**: See `docs/development/ai-subpackage-design.md`
- **Issue Tracker**: https://github.com/jbdevprimary/vendor-connectors/issues
- **Examples**: See test files in `tests/ai/`

## Summary

The `vendor_connectors.ai` sub-package is designed for agent workflows with tools and multi-provider support. The `vendor_connectors.anthropic` connector remains the best choice for simple, direct Anthropic API access with minimal dependencies.

Choose based on your needs:
- **Simple chat** → anthropic connector
- **Agent with tools** → AI sub-package
- **Both** → Use both packages together
