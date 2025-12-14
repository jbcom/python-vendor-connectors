"""AI framework tools for Google Cloud and Workspace operations.

This module provides tools for Google Cloud and Workspace operations that work
with multiple AI agent frameworks. The core functions are framework-agnostic
Python functions, with native wrappers for each supported framework.

Supported Frameworks:
- LangChain (via langchain-core) - get_langchain_tools()
- CrewAI - get_crewai_tools()
- AWS Strands - get_strands_tools() (plain functions)
- Auto-detection - get_tools() picks the best available

Tools provided:
- google_list_projects: List GCP projects
- google_list_enabled_services: List enabled services in a project
- google_list_billing_accounts: List billing accounts
- google_list_workspace_users: List Workspace users
- google_list_workspace_groups: List Workspace groups

Usage:
    from vendor_connectors.google.tools import get_tools
    tools = get_tools()  # Returns best format for installed framework
"""

from __future__ import annotations

from typing import Any

# =============================================================================
# Tool Implementation Functions
# =============================================================================


def list_projects(
    parent: str = "",
    max_results: int = 100,
) -> list[dict[str, Any]]:
    """List Google Cloud projects.

    Args:
        parent: Parent resource (e.g., 'organizations/123' or 'folders/456').
                Leave empty to list all accessible projects.
        max_results: Maximum number of projects to return.

    Returns:
        List of project info (project_id, name, state, parent).
    """
    from vendor_connectors.google import GoogleConnectorFull

    connector = GoogleConnectorFull()
    projects = connector.list_projects(parent=parent if parent else None)

    # Limit results and extract key fields
    result = []
    for project in projects[:max_results]:
        result.append(
            {
                "project_id": project.get("projectId", ""),
                "name": project.get("displayName") or project.get("name", ""),
                "state": project.get("state", ""),
                "parent": project.get("parent", ""),
            }
        )

    return result


def list_enabled_services(
    project_id: str,
    max_results: int = 100,
) -> list[dict[str, Any]]:
    """List enabled services in a Google Cloud project.

    Args:
        project_id: The GCP project ID to list services for.
        max_results: Maximum number of services to return.

    Returns:
        List of service info (name, title, state).
    """
    from vendor_connectors.google import GoogleConnectorFull

    connector = GoogleConnectorFull()
    services = connector.list_enabled_services(project_id=project_id)

    # Limit results and extract key fields
    result = []
    for service in services[:max_results]:
        result.append(
            {
                "name": service.get("name", ""),
                "title": service.get("config", {}).get("title", ""),
                "state": service.get("state", ""),
            }
        )

    return result


def list_billing_accounts(
    max_results: int = 100,
) -> list[dict[str, Any]]:
    """List Google Cloud billing accounts.

    Args:
        max_results: Maximum number of billing accounts to return.

    Returns:
        List of billing account info (name, display_name, open, master_billing_account).
    """
    from vendor_connectors.google import GoogleConnectorFull

    connector = GoogleConnectorFull()
    accounts = connector.list_billing_accounts()

    # Limit results and extract key fields
    result = []
    for account in accounts[:max_results]:
        result.append(
            {
                "name": account.get("name", ""),
                "display_name": account.get("displayName", ""),
                "open": account.get("open", False),
                "master_billing_account": account.get("masterBillingAccount", ""),
            }
        )

    return result


def list_workspace_users(
    domain: str = "",
    max_results: int = 100,
) -> list[dict[str, Any]]:
    """List users from Google Workspace.

    Args:
        domain: Domain to list users from. Leave empty for default domain.
        max_results: Maximum number of users to return.

    Returns:
        List of user info (email, name, full_name, suspended, org_unit_path).
    """
    from vendor_connectors.google import GoogleConnectorFull

    connector = GoogleConnectorFull()
    users = connector.list_users(
        domain=domain if domain else None,
        flatten_names=True,
        key_by_email=False,
    )

    # Limit results and extract key fields
    result = []
    for user in users[:max_results]:
        result.append(
            {
                "email": user.get("primaryEmail", ""),
                "name": user.get("name", {}).get("fullName", "") if isinstance(user.get("name"), dict) else "",
                "full_name": user.get("full_name", ""),
                "suspended": user.get("suspended", False),
                "org_unit_path": user.get("orgUnitPath", ""),
            }
        )

    return result


def list_workspace_groups(
    domain: str = "",
    max_results: int = 100,
) -> list[dict[str, Any]]:
    """List groups from Google Workspace.

    Args:
        domain: Domain to list groups from. Leave empty for default domain.
        max_results: Maximum number of groups to return.

    Returns:
        List of group info (email, name, description, direct_members_count).
    """
    from vendor_connectors.google import GoogleConnectorFull

    connector = GoogleConnectorFull()
    groups = connector.list_groups(
        domain=domain if domain else None,
        key_by_email=False,
    )

    # Limit results and extract key fields
    result = []
    for group in groups[:max_results]:
        result.append(
            {
                "email": group.get("email", ""),
                "name": group.get("name", ""),
                "description": group.get("description", ""),
                "direct_members_count": group.get("directMembersCount", 0),
            }
        )

    return result


# =============================================================================
# Tool Definitions
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "google_list_projects",
        "description": "List Google Cloud projects with their IDs, names, and states.",
        "func": list_projects,
    },
    {
        "name": "google_list_enabled_services",
        "description": "List enabled APIs/services in a Google Cloud project.",
        "func": list_enabled_services,
    },
    {
        "name": "google_list_billing_accounts",
        "description": "List Google Cloud billing accounts with their status.",
        "func": list_billing_accounts,
    },
    {
        "name": "google_list_workspace_users",
        "description": "List users from Google Workspace with their details.",
        "func": list_workspace_users,
    },
    {
        "name": "google_list_workspace_groups",
        "description": "List groups from Google Workspace with member counts.",
        "func": list_workspace_groups,
    },
]


# =============================================================================
# Framework-Specific Getters
# =============================================================================


def get_langchain_tools() -> list[Any]:
    """Get all Google tools as LangChain StructuredTools.

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
    """Get all Google tools as CrewAI tools.

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
    """Get all Google tools as plain Python functions for AWS Strands.

    Returns:
        List of callable functions.
    """
    return [defn["func"] for defn in TOOL_DEFINITIONS]


def get_tools(framework: str = "auto") -> list[Any]:
    """Get Google tools for the specified or auto-detected framework.

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
    "list_projects",
    "list_enabled_services",
    "list_billing_accounts",
    "list_workspace_users",
    "list_workspace_groups",
    # Tool metadata
    "TOOL_DEFINITIONS",
]
