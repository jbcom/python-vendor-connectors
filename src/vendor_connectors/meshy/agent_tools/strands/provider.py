"""Strands Agents SDK tool provider implementation.

This module converts mesh-toolkit's generic tool definitions into
Strands-compatible tool functions using the @tool decorator pattern.
"""

from __future__ import annotations

from typing import Any

# Import to register tools
import vendor_connectors.meshy.agent_tools.tools  # noqa: F401
from vendor_connectors.meshy.agent_tools.base import (
    BaseToolProvider,
    ToolDefinition,
    get_tool_definitions,
)


def _create_strands_tool(definition: ToolDefinition) -> Any:
    """Create a Strands tool from a tool definition.

    Strands uses a simple @tool decorator pattern. We create a function
    with proper signature and docstring that wraps the handler.
    """
    try:
        from strands import tool
    except ImportError as e:
        raise ImportError(
            "strands-agents is required. Install with: pip install vendor-connectors[strands]"
        ) from e

    # Build parameter info for docstring
    param_docs = []
    for param_name, param in definition.parameters.items():
        req = "Required" if param.required else f"Optional, default={param.default}"
        param_docs.append(f"    {param_name}: {param.description} ({req})")

    docstring = f"""{definition.description}

Args:
{chr(10).join(param_docs) if param_docs else "    None"}

Returns:
    JSON string with result data
"""

    # Create wrapper function
    handler = definition.handler

    def tool_func(**kwargs) -> str:
        return handler(**kwargs)

    # Set function metadata
    tool_func.__name__ = definition.name
    tool_func.__doc__ = docstring

    # Apply Strands @tool decorator
    return tool(tool_func)


class StrandsToolProvider(BaseToolProvider):
    """Strands tool provider for mesh-toolkit.

    Converts generic tool definitions into Strands-compatible tools.

    Usage:
        provider = StrandsToolProvider()
        tools = provider.get_tools()

        # Use with Strands Agent
        from strands import Agent
        agent = Agent(tools=tools)
    """

    def __init__(self):
        self._tools: dict[str, Any] = {}

    @property
    def name(self) -> str:
        return "strands"

    @property
    def version(self) -> str:
        return "1.0.0"

    def _ensure_tools_created(self) -> None:
        """Create tools if not already done."""
        if self._tools:
            return

        for definition in get_tool_definitions():
            try:
                strands_tool = _create_strands_tool(definition)
                self._tools[definition.name] = strands_tool
            except ImportError:
                # Strands not installed
                pass

    def get_tools(self) -> list[Any]:
        """Get all tools as Strands tool functions.

        Returns:
            List of Strands tool functions
        """
        self._ensure_tools_created()
        return list(self._tools.values())

    def get_tool(self, name: str) -> Any | None:
        """Get a specific tool by name.

        Args:
            name: Tool name (e.g., 'text3d_generate')

        Returns:
            Strands tool function or None
        """
        self._ensure_tools_created()
        return self._tools.get(name)


# Module-level convenience functions
_provider: StrandsToolProvider | None = None


def _get_provider() -> StrandsToolProvider:
    """Get or create the singleton provider."""
    global _provider
    if _provider is None:
        _provider = StrandsToolProvider()
    return _provider


def get_tools() -> list[Any]:
    """Get all mesh-toolkit tools as Strands tool functions.

    Usage:
        from vendor_connectors.meshy.agent_tools.strands import get_tools

        tools = get_tools()
        agent = Agent(tools=tools)

    Returns:
        List of Strands tool functions
    """
    return _get_provider().get_tools()


def get_tool(name: str) -> Any | None:
    """Get a specific tool by name.

    Args:
        name: Tool name (e.g., 'text3d_generate', 'list_animations')

    Returns:
        Strands tool function or None if not found
    """
    return _get_provider().get_tool(name)
