"""Unified MCP Server for Vendor Connectors.

This module provides a single MCP (Model Context Protocol) server that
exposes ALL vendor connectors as tools via the registry.

Usage:
    # Command line
    vendor-connectors-mcp

    # Or programmatically
    from vendor_connectors.mcp import create_server, main
    server = create_server()

The server automatically discovers all registered connectors and exposes
their public methods as MCP tools.

This provides the bridge between TypeScript (@agentic/control) and Python
with zero custom code - just standard MCP over stdio.
"""

from __future__ import annotations

import inspect
import json
from typing import Any, Callable

from vendor_connectors.registry import get_connector, list_connectors


def _check_mcp_installed() -> bool:
    """Check if MCP SDK is installed."""
    try:
        from mcp.server import Server  # noqa: F401

        return True
    except ImportError:
        return False


def _get_method_schema(method: Callable) -> dict[str, Any]:
    """Generate JSON schema from method signature."""
    sig = inspect.signature(method)
    properties = {}
    required = []

    for name, param in sig.parameters.items():
        if name in ("self", "cls"):
            continue

        prop: dict[str, Any] = {"type": "string"}  # Default

        # Try to get type from annotations
        if param.annotation != inspect.Parameter.empty:
            ann = param.annotation
            if ann is int:
                prop = {"type": "integer"}
            elif ann is float:
                prop = {"type": "number"}
            elif ann is bool:
                prop = {"type": "boolean"}
            elif ann is list or (hasattr(ann, "__origin__") and ann.__origin__ is list):
                prop = {"type": "array"}
            elif ann is dict or (hasattr(ann, "__origin__") and ann.__origin__ is dict):
                prop = {"type": "object"}

        # Get description from docstring if available
        if method.__doc__:
            # Simple extraction - look for "name:" in docstring
            for line in method.__doc__.split("\n"):
                if f"{name}:" in line.lower():
                    prop["description"] = line.split(":", 1)[-1].strip()
                    break

        # Handle defaults
        if param.default != inspect.Parameter.empty:
            prop["default"] = param.default
        else:
            required.append(name)

        properties[name] = prop

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _get_public_methods(connector_class: type) -> list[tuple[str, Callable]]:
    """Get public methods from a connector class (excluding dunder and private)."""
    methods = []
    for name in dir(connector_class):
        if name.startswith("_"):
            continue
        attr = getattr(connector_class, name, None)
        if callable(attr) and not isinstance(attr, type):
            methods.append((name, attr))
    return methods


def create_server():
    """Create the unified MCP server with all registered connectors."""
    try:
        from mcp.server import Server
        from mcp.types import TextContent, Tool
    except ImportError as e:
        raise ImportError("MCP SDK not installed. Install with: pip install vendor-connectors[mcp]") from e

    server = Server("vendor-connectors")

    # Build tool registry from all connectors
    TOOLS: dict[str, dict[str, Any]] = {}

    # Discover all connectors
    connectors = list_connectors()

    for connector_name, connector_class in connectors.items():
        # Get public methods
        for method_name, method in _get_public_methods(connector_class):
            # Skip common base class methods
            if method_name in ("close", "request", "get_input", "register_tool"):
                continue

            tool_name = f"{connector_name}_{method_name}"

            # Get method from class (unbound)
            try:
                schema = _get_method_schema(method)
            except Exception:
                schema = {"type": "object", "properties": {}}

            # Get description from docstring
            description = ""
            if method.__doc__:
                description = method.__doc__.split("\n")[0].strip()
            if not description:
                description = f"{connector_name}.{method_name}()"

            TOOLS[tool_name] = {
                "connector": connector_name,
                "method": method_name,
                "description": description,
                "parameters": schema,
            }

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """Return all available tools."""
        return [
            Tool(name=name, description=tool["description"], inputSchema=tool["parameters"])
            for name, tool in TOOLS.items()
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Execute a tool and return results."""
        if name not in TOOLS:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        tool = TOOLS[name]
        connector_name = tool["connector"]
        method_name = tool["method"]

        try:
            # Instantiate connector (will get credentials from env)
            connector = get_connector(connector_name)

            # Get and call the method
            method = getattr(connector, method_name)
            result = method(**arguments)

            # Handle async methods
            if inspect.iscoroutine(result):
                result = await result

            # Convert Pydantic models to dict
            if hasattr(result, "model_dump"):
                result = result.model_dump()
            elif hasattr(result, "__iter__") and not isinstance(result, (str, dict)):
                result = [r.model_dump() if hasattr(r, "model_dump") else r for r in result]

            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]

    return server


def main() -> int:
    """Run the MCP server over stdio."""
    import asyncio

    try:
        from mcp.server.stdio import stdio_server
    except ImportError:
        print("MCP SDK not installed. Install with: pip install vendor-connectors[mcp]")
        return 1

    server = create_server()

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(run())
    return 0


if __name__ == "__main__":
    exit(main())
