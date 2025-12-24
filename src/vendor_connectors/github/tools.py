"""AI framework tools for GitHub operations.

This module provides tools for GitHub operations that work with multiple
AI agent frameworks.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

# =============================================================================
# Input Schemas
# =============================================================================


class GetRepositoryFileSchema(BaseModel):
    """Schema for getting a file from GitHub."""

    owner: str = Field(..., description="The GitHub owner (user or organization).")
    repo: str = Field(..., description="The repository name.")
    path: str = Field(..., description="The path to the file in the repository.")
    branch: Optional[str] = Field(None, description="The branch to get the file from.")


class UpdateRepositoryFileSchema(BaseModel):
    """Schema for updating a file on GitHub."""

    owner: str = Field(..., description="The GitHub owner.")
    repo: str = Field(..., description="The repository name.")
    path: str = Field(..., description="The path to the file.")
    content: str = Field(..., description="The new content for the file.")
    message: str = Field(..., description="The commit message.")
    branch: Optional[str] = Field(None, description="The branch to update.")


class ListOrgMembersSchema(BaseModel):
    """Schema for listing GitHub organization members."""

    owner: str = Field(..., description="The GitHub organization name.")
    role: Optional[str] = Field(None, description="Filter by role ('admin', 'member').")


# =============================================================================
# Tool Implementation Functions
# =============================================================================


def github_get_file(
    owner: str,
    repo: str,
    path: str,
    branch: Optional[str] = None,
) -> Any:
    """Get a file from a GitHub repository.

    Args:
        owner: GitHub owner.
        repo: Repository name.
        path: File path.
        branch: Optional branch name.

    Returns:
        The decoded file content (dict if JSON/YAML, str otherwise).
    """
    from vendor_connectors.github import GithubConnector

    connector = GithubConnector(github_owner=owner, github_repo=repo, github_branch=branch)
    return connector.get_repository_file(file_path=path)


def github_update_file(
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: Optional[str] = None,
) -> dict[str, Any]:
    """Create or update a file in a GitHub repository.

    Args:
        owner: GitHub owner.
        repo: Repository name.
        path: File path.
        content: New file content.
        message: Commit message.
        branch: Optional branch name.

    Returns:
        GitHub API response metadata.
    """
    from vendor_connectors.github import GithubConnector

    connector = GithubConnector(github_owner=owner, github_repo=repo, github_branch=branch)
    return connector.update_repository_file(file_path=path, file_data=content, msg=message)


def github_list_org_members(
    owner: str,
    role: Optional[str] = None,
) -> list[dict[str, Any]]:
    """List members of a GitHub organization.

    Args:
        owner: Organization name.
        role: Optional role filter.

    Returns:
        List of member profiles.
    """
    from vendor_connectors.github import GithubConnector

    connector = GithubConnector(github_owner=owner)
    members = connector.list_org_members(role=role)
    return list(members.values())


def github_list_repositories(
    owner: str,
) -> list[dict[str, Any]]:
    """List repositories for a GitHub organization or user.

    Args:
        owner: GitHub owner.

    Returns:
        List of repository metadata.
    """
    from vendor_connectors.github import GithubConnector

    connector = GithubConnector(github_owner=owner)
    repos = connector.list_repositories()
    return list(repos.values())


# =============================================================================
# Tool Definitions
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "github_get_file",
        "description": "Read a file from a GitHub repository. Automatically decodes JSON and YAML.",
        "func": github_get_file,
        "args_schema": GetRepositoryFileSchema,
    },
    {
        "name": "github_update_file",
        "description": "Create or update a file in a GitHub repository with a commit message.",
        "func": github_update_file,
        "args_schema": UpdateRepositoryFileSchema,
    },
    {
        "name": "github_list_org_members",
        "description": "List all members of a GitHub organization.",
        "func": github_list_org_members,
        "args_schema": ListOrgMembersSchema,
    },
    {
        "name": "github_list_repositories",
        "description": "List repositories for a given GitHub owner.",
        "func": github_list_repositories,
    },
]


# =============================================================================
# Framework-Specific Getters
# =============================================================================


def get_langchain_tools() -> list[Any]:
    """Get all GitHub tools as LangChain StructuredTools."""
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
    """Get all GitHub tools as CrewAI tools."""
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
    """Get all GitHub tools as plain Python functions."""
    return [defn["func"] for defn in TOOL_DEFINITIONS]


def get_tools(framework: str = "auto") -> list[Any]:
    """Get GitHub tools for the specified or auto-detected framework."""
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
    "github_get_file",
    "github_update_file",
    "github_list_org_members",
    "github_list_repositories",
    "TOOL_DEFINITIONS",
]
