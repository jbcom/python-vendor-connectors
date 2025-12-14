"""Agent tools for mesh-toolkit - AI agent integrations for 3D asset generation.

This subpackage provides integrations with various AI agent frameworks:
- CrewAI tools (pip install vendor-connectors[crewai])
- MCP (Model Context Protocol) server (pip install vendor-connectors[mcp])
- Strands Agents SDK (pip install vendor-connectors[strands])
- LangChain tools via ai/ subpackage (pip install vendor-connectors[ai])

Architecture:
    agent_tools/
        __init__.py          # This file - registry and exports
        base.py              # Base classes and interfaces (framework-agnostic)
        tools.py             # Core tool implementations
        registry.py          # Tool provider registry
        crewai/              # CrewAI-specific provider
        mcp/                 # MCP server provider
        strands/             # Strands Agents SDK provider

Usage:
    # CrewAI integration
    from vendor_connectors.meshy.agent_tools.crewai import get_tools
    tools = get_tools()
    agent = Agent(role="Artist", tools=tools, ...)

    # Strands integration
    from vendor_connectors.meshy.agent_tools.strands import get_tools
    tools = get_tools()
    agent = Agent(tools=tools)

    # MCP server
    from vendor_connectors.meshy.agent_tools.mcp import create_server
    server = create_server()

    # Registry for all providers
    from vendor_connectors.meshy.agent_tools import get_provider, list_providers
    providers = list_providers()  # ['crewai', 'mcp', 'strands']

Dependency Direction:
    This package PROVIDES tools that consumers (like agentic-crew) can use.
    vendor-connectors does NOT depend on crew orchestration packages.
    Instead, orchestration packages should depend on vendor-connectors.
"""

from __future__ import annotations

from vendor_connectors.meshy.agent_tools.registry import (
    ToolProvider,
    get_provider,
    list_providers,
    register_provider,
)

__all__ = [
    "ToolProvider",
    "get_provider",
    "list_providers",
    "register_provider",
]
