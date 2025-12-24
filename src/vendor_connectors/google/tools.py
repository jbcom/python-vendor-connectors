"""AI framework tools for Google Cloud and Workspace operations.

This module provides tools for Google operations that work with multiple
AI agent frameworks.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

# =============================================================================
# Input Schemas
# =============================================================================


class ListUsersSchema(BaseModel):
    """Schema for listing Google Workspace users."""

    domain: Optional[str] = Field(None, description="The domain to list users from.")
    max_results: int = Field(100, description="Maximum number of users to return.")
    include_suspended: bool = Field(False, description="Whether to include suspended users.")


class ListProjectsSchema(BaseModel):
    """Schema for listing Google Cloud projects."""

    parent: Optional[str] = Field(None, description="Parent resource (organizations/ORG_ID or folders/FOLDER_ID).")
    filter_query: Optional[str] = Field(None, description="Optional filter query string.")


class CreateProjectSchema(BaseModel):
    """Schema for creating a Google Cloud project."""

    project_id: str = Field(..., description="Unique project ID.")
    display_name: str = Field(..., description="Human-readable project name.")
    parent: Optional[str] = Field(None, description="Parent resource (organizations/ORG_ID or folders/FOLDER_ID).")


# =============================================================================
# Tool Implementation Functions
# =============================================================================


def google_list_users(
    domain: Optional[str] = None,
    max_results: int = 100,
    include_suspended: bool = False,
) -> list[dict[str, Any]]:
    """List users from Google Workspace.

    Args:
        domain: Domain filter.
        max_results: Max results.
        include_suspended: Include suspended users.

    Returns:
        List of user profiles.
    """
    from vendor_connectors.google import GoogleConnectorFull

    connector = GoogleConnectorFull()
    users = connector.list_users(domain=domain, max_results=max_results, include_suspended=include_suspended)
    return users if isinstance(users, list) else list(users.values())


def google_list_projects(
    parent: Optional[str] = None,
    filter_query: Optional[str] = None,
) -> list[dict[str, Any]]:
    """List Google Cloud projects.

    Args:
        parent: Parent resource ID.
        filter_query: Filter string.

    Returns:
        List of project metadata.
    """
    from vendor_connectors.google import GoogleConnectorFull

    connector = GoogleConnectorFull()
    return connector.list_projects(parent=parent, filter_query=filter_query)


def google_create_project(
    project_id: str,
    display_name: str,
    parent: Optional[str] = None,
) -> dict[str, Any]:
    """Create a new Google Cloud project.

    Args:
        project_id: Unique project ID.
        display_name: Project display name.
        parent: Parent resource ID.

    Returns:
        Operation response.
    """
    from vendor_connectors.google import GoogleConnectorFull

    connector = GoogleConnectorFull()
    return connector.create_project(project_id=project_id, display_name=display_name, parent=parent)


def google_list_folders(parent: str) -> list[dict[str, Any]]:
    """List folders under a Google Cloud parent.

    Args:
        parent: Parent resource ID (organizations/ORG_ID or folders/FOLDER_ID).

    Returns:
        List of folder metadata.
    """
    from vendor_connectors.google import GoogleConnectorFull

    connector = GoogleConnectorFull()
    return connector.list_folders(parent=parent)


# =============================================================================
# Tool Definitions
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "google_list_users",
        "description": "List users in Google Workspace (Admin Directory).",
        "func": google_list_users,
        "args_schema": ListUsersSchema,
    },
    {
        "name": "google_list_projects",
        "description": "List Google Cloud Platform projects.",
        "func": google_list_projects,
        "args_schema": ListProjectsSchema,
    },
    {
        "name": "google_create_project",
        "description": "Create a new Google Cloud Platform project.",
        "func": google_create_project,
        "args_schema": CreateProjectSchema,
    },
    {
        "name": "google_list_folders",
        "description": "List folders in Google Cloud Resource Manager.",
        "func": google_list_folders,
    },
]


# =============================================================================
# Framework-Specific Getters
# =============================================================================


def get_langchain_tools() -> list[Any]:
    """Get all Google tools as LangChain StructuredTools."""
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
    """Get all Google tools as CrewAI tools."""
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
    """Get all Google tools as plain Python functions."""
    return [defn["func"] for defn in TOOL_DEFINITIONS]


def get_tools(framework: str = "auto") -> list[Any]:
    """Get Google tools for the specified or auto-detected framework."""
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
    "google_list_users",
    "google_list_projects",
    "google_create_project",
    "google_list_folders",
    "TOOL_DEFINITIONS",
]
