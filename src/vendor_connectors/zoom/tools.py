"""AI framework tools for Zoom operations.

This module provides tools for Zoom operations that work with multiple
AI agent frameworks.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# Input Schemas
# =============================================================================


class CreateZoomUserSchema(BaseModel):
    """Schema for creating a Zoom user."""

    email: str = Field(..., description="The email address of the user to create.")
    first_name: str = Field(..., description="User's first name.")
    last_name: str = Field(..., description="User's last name.")


class RemoveZoomUserSchema(BaseModel):
    """Schema for removing a Zoom user."""

    email: str = Field(..., description="The email address of the user to remove.")


# =============================================================================
# Tool Implementation Functions
# =============================================================================


def zoom_list_users() -> list[dict[str, Any]]:
    """List all Zoom users in the account.

    Returns:
        List of user dictionaries.
    """
    from vendor_connectors.zoom import ZoomConnector

    connector = ZoomConnector()
    users = connector.get_zoom_users()
    return list(users.values())


def zoom_create_user(
    email: str,
    first_name: str,
    last_name: str,
) -> bool:
    """Create a new Zoom user with a paid license.

    Args:
        email: User email.
        first_name: First name.
        last_name: Last name.

    Returns:
        True if successful, False otherwise.
    """
    from vendor_connectors.zoom import ZoomConnector

    connector = ZoomConnector()
    return connector.create_zoom_user(email=email, first_name=first_name, last_name=last_name)


def zoom_remove_user(email: str) -> bool:
    """Remove a Zoom user.

    Args:
        email: Email of the user to remove.

    Returns:
        True if successful.
    """
    from vendor_connectors.zoom import ZoomConnector

    connector = ZoomConnector()
    connector.remove_zoom_user(email=email)
    return len(connector.errors) == 0


# =============================================================================
# Tool Definitions
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "zoom_list_users",
        "description": "List all users in the Zoom account. Useful for auditing or finding users.",
        "func": zoom_list_users,
    },
    {
        "name": "zoom_create_user",
        "description": "Create a new Zoom user with a paid (Licensed) status.",
        "func": zoom_create_user,
        "args_schema": CreateZoomUserSchema,
    },
    {
        "name": "zoom_remove_user",
        "description": "Remove a user from the Zoom account.",
        "func": zoom_remove_user,
        "args_schema": RemoveZoomUserSchema,
    },
]


# =============================================================================
# Framework-Specific Getters
# =============================================================================


def get_langchain_tools() -> list[Any]:
    """Get all Zoom tools as LangChain StructuredTools."""
    try:
        from langchain_core.tools import StructuredTool
    except ImportError as e:
        raise ImportError("langchain-core is required for LangChain tools.") from e

    return [
        StructuredTool.from_function(
            func=defn["func"],
            name=defn["name"],
            description=defn["description"],
            args_schema=defn.get("args_schema"),
        )
        for defn in TOOL_DEFINITIONS
    ]


def get_crewai_tools() -> list[Any]:
    """Get all Zoom tools as CrewAI tools."""
    try:
        from crewai.tools import tool as crewai_tool
    except ImportError as e:
        raise ImportError("crewai is required for CrewAI tools.") from e

    tools = []
    for defn in TOOL_DEFINITIONS:
        wrapped = crewai_tool(defn["name"])(defn["func"])
        wrapped.description = defn["description"]
        if "args_schema" in defn:
            wrapped.args_schema = defn["args_schema"]
        tools.append(wrapped)

    return tools


def get_strands_tools() -> list[Any]:
    """Get all Zoom tools as plain Python functions."""
    return [defn["func"] for defn in TOOL_DEFINITIONS]


def get_tools(framework: str = "auto") -> list[Any]:
    """Get Zoom tools for the specified or auto-detected framework."""
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

    raise ValueError(f"Unknown framework: {framework}")


__all__ = [
    "get_tools",
    "get_langchain_tools",
    "get_crewai_tools",
    "get_strands_tools",
    "zoom_list_users",
    "zoom_create_user",
    "zoom_remove_user",
    "TOOL_DEFINITIONS",
]
