"""AI framework tools for Vault operations.

This module provides tools for Vault operations that work with multiple
AI agent frameworks. The core functions are framework-agnostic Python functions,
with native wrappers for each supported framework.

Supported Frameworks:
- LangChain (via langchain-core) - get_langchain_tools()
- CrewAI - get_crewai_tools()
- AWS Strands - get_strands_tools() (plain functions)
- Auto-detection - get_tools() picks the best available

Tools provided:
- vault_list_secrets: List secrets at a path in Vault KV v2
- vault_read_secret: Read a single secret from Vault

Usage:
    from vendor_connectors.vault.tools import get_tools
    tools = get_tools()  # Returns best format for installed framework
"""

from __future__ import annotations

from typing import Any

# =============================================================================
# Tool Implementation Functions
# =============================================================================


def list_secrets(
    root_path: str = "/",
    mount_point: str = "secret",
    max_depth: int = 10,
) -> list[dict[str, Any]]:
    """List secrets recursively from Vault KV v2 engine.

    Args:
        root_path: Starting path for listing (default: "/")
        mount_point: KV engine mount point (default: "secret")
        max_depth: Maximum directory depth to traverse (default: 10)

    Returns:
        List of secrets with their paths and data
    """
    from vendor_connectors.vault import VaultConnector

    connector = VaultConnector()
    secrets = connector.list_secrets(
        root_path=root_path,
        mount_point=mount_point,
        max_depth=max_depth,
    )

    # Transform to list format for easier consumption
    result = []
    for path, data in secrets.items():
        result.append(
            {
                "path": path,
                "mount_point": mount_point,
                "data": data,
                "key_count": len(data) if isinstance(data, dict) else 0,
            }
        )

    return result


def read_secret(
    path: str,
    mount_point: str = "secret",
) -> dict[str, Any]:
    """Read a single secret from Vault KV v2.

    Args:
        path: Path to the secret
        mount_point: KV engine mount point (default: "secret")

    Returns:
        Dict with path, mount_point, data, and found status
    """
    from vendor_connectors.vault import VaultConnector

    connector = VaultConnector()
    secret_data = connector.read_secret(
        path=path,
        mount_point=mount_point,
    )

    return {
        "path": path,
        "mount_point": mount_point,
        "data": secret_data if secret_data else {},
        "found": secret_data is not None,
    }


# =============================================================================
# Tool Definitions
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "vault_list_secrets",
        "description": "List secrets recursively from Vault KV v2 engine. Returns secret paths and their data.",
        "func": list_secrets,
    },
    {
        "name": "vault_read_secret",
        "description": "Read a single secret from Vault KV v2 by path. Returns the secret data.",
        "func": read_secret,
    },
]


# =============================================================================
# Framework-Specific Getters
# =============================================================================


def get_langchain_tools() -> list[Any]:
    """Get all Vault tools as LangChain StructuredTools.

    Returns:
        List of LangChain StructuredTool objects.

    Raises:
        ImportError: If langchain-core is not installed.
    """
    try:
        from langchain_core.tools import StructuredTool
    except ImportError as e:
        raise ImportError(
            "langchain-core is required for LangChain tools.\nInstall with: pip install vendor-connectors[langchain]"
        ) from e

    return [
        StructuredTool.from_function(
            func=defn["func"],
            name=defn["name"],
            description=defn["description"],
        )
        for defn in TOOL_DEFINITIONS
    ]


def get_crewai_tools() -> list[Any]:
    """Get all Vault tools as CrewAI tools.

    Returns:
        List of CrewAI BaseTool objects.

    Raises:
        ImportError: If crewai is not installed.
    """
    try:
        from crewai.tools import tool as crewai_tool
    except ImportError as e:
        raise ImportError(
            "crewai is required for CrewAI tools.\nInstall with: pip install vendor-connectors[crewai]"
        ) from e

    tools = []
    for defn in TOOL_DEFINITIONS:
        wrapped = crewai_tool(defn["name"])(defn["func"])
        wrapped.description = defn["description"]
        tools.append(wrapped)

    return tools


def get_strands_tools() -> list[Any]:
    """Get all Vault tools as plain Python functions for AWS Strands.

    Returns:
        List of callable functions.
    """
    return [defn["func"] for defn in TOOL_DEFINITIONS]


def get_tools(framework: str = "auto") -> list[Any]:
    """Get Vault tools for the specified or auto-detected framework.

    Args:
        framework: Framework to use. Options:
            - "auto" (default): Auto-detect based on installed packages
            - "langchain": Force LangChain StructuredTools
            - "crewai": Force CrewAI tools
            - "strands": Force plain functions for Strands
            - "functions": Force plain functions (alias for strands)

    Returns:
        List of tools in the appropriate format for the framework.

    Raises:
        ImportError: If the requested framework is not installed.
        ValueError: If an unknown framework is specified.
    """
    from vendor_connectors._compat import is_available

    if framework == "auto":
        if is_available("crewai"):
            return get_crewai_tools()
        if is_available("langchain_core"):
            return get_langchain_tools()
        return get_strands_tools()

    if framework == "langchain":
        return get_langchain_tools()
    if framework == "crewai":
        return get_crewai_tools()
    if framework in ("strands", "functions"):
        return get_strands_tools()

    raise ValueError(f"Unknown framework: {framework}. Options: auto, langchain, crewai, strands, functions")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Framework-specific getters
    "get_tools",
    "get_langchain_tools",
    "get_crewai_tools",
    "get_strands_tools",
    # Raw functions
    "list_secrets",
    "read_secret",
    # Tool metadata
    "TOOL_DEFINITIONS",
]
