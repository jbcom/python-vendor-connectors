"""AI framework tools for GitHub operations.

This module provides tools for GitHub operations that work with
multiple AI agent frameworks.

Supported Frameworks:
- LangChain (via langchain-core) - get_langchain_tools()
- CrewAI - get_crewai_tools()
- AWS Strands - get_strands_tools() (plain functions)
- Auto-detection - get_tools() picks the best available

Tools provided:
- github_list_repositories: List repositories in the organization
- github_get_repository: Get repository details
- github_list_teams: List teams in the organization
- github_get_team: Get team details
- github_list_org_members: List organization members
- github_get_repository_file: Get file contents from a repository

Usage:
    from vendor_connectors.github.tools import get_tools
    tools = get_tools()  # Returns best format for installed framework
"""

from __future__ import annotations

from typing import Any, Optional

# =============================================================================
# Tool Implementation Functions
# =============================================================================


def list_repositories(
    github_owner: str,
    github_token: str,
    type_filter: str = "all",
    include_branches: bool = False,
) -> list[dict[str, Any]]:
    """List repositories in the GitHub organization.

    Args:
        github_owner: GitHub organization name
        github_token: GitHub personal access token
        type_filter: Filter type ('all', 'public', 'private', 'forks', 'sources', 'member')
        include_branches: Include branch information. Defaults to False.

    Returns:
        List of repository information (name, description, url, etc.)
    """
    from vendor_connectors.github import GithubConnector

    connector = GithubConnector(github_owner=github_owner, github_token=github_token)
    repos = connector.list_repositories(type_filter=type_filter, include_branches=include_branches)

    # Convert dict to list
    result = []
    for name, data in repos.items():
        result.append(
            {
                "name": name,
                "full_name": data.get("full_name", ""),
                "description": data.get("description", ""),
                "private": data.get("private", False),
                "archived": data.get("archived", False),
                "default_branch": data.get("default_branch", ""),
                "html_url": data.get("html_url", ""),
                "language": data.get("language", ""),
                "topics": data.get("topics", []),
            }
        )

    return result


def get_repository(
    github_owner: str,
    github_token: str,
    repo_name: str,
) -> Optional[dict[str, Any]]:
    """Get a specific repository details.

    Args:
        github_owner: GitHub organization name
        github_token: GitHub personal access token
        repo_name: Repository name

    Returns:
        Repository information or None if not found
    """
    from vendor_connectors.github import GithubConnector

    connector = GithubConnector(github_owner=github_owner, github_token=github_token)
    repo = connector.get_repository(repo_name)

    return repo


def list_teams(
    github_owner: str,
    github_token: str,
    include_members: bool = False,
    include_repos: bool = False,
) -> list[dict[str, Any]]:
    """List teams in the GitHub organization.

    Args:
        github_owner: GitHub organization name
        github_token: GitHub personal access token
        include_members: Include team members. Defaults to False.
        include_repos: Include team repositories. Defaults to False.

    Returns:
        List of team information (name, slug, description, etc.)
    """
    from vendor_connectors.github import GithubConnector

    connector = GithubConnector(github_owner=github_owner, github_token=github_token)
    teams = connector.list_teams(include_members=include_members, include_repos=include_repos)

    # Convert dict to list
    result = []
    for slug, data in teams.items():
        result.append(
            {
                "slug": slug,
                "name": data.get("name", ""),
                "description": data.get("description", ""),
                "privacy": data.get("privacy", ""),
                "permission": data.get("permission", ""),
                "html_url": data.get("html_url", ""),
                "members_count": data.get("members_count", 0),
                "repos_count": data.get("repos_count", 0),
            }
        )

    return result


def get_team(
    github_owner: str,
    github_token: str,
    team_slug: str,
) -> Optional[dict[str, Any]]:
    """Get a specific team details.

    Args:
        github_owner: GitHub organization name
        github_token: GitHub personal access token
        team_slug: Team slug

    Returns:
        Team information or None if not found
    """
    from vendor_connectors.github import GithubConnector

    connector = GithubConnector(github_owner=github_owner, github_token=github_token)
    team = connector.get_team(team_slug)

    return team


def list_org_members(
    github_owner: str,
    github_token: str,
    role: Optional[str] = None,
    include_pending: bool = False,
) -> list[dict[str, Any]]:
    """List members in the GitHub organization.

    Args:
        github_owner: GitHub organization name
        github_token: GitHub personal access token
        role: Filter by role ('admin', 'member'). None returns all.
        include_pending: Include pending invitations. Defaults to False.

    Returns:
        List of member information (login, name, email, role, etc.)
    """
    from vendor_connectors.github import GithubConnector

    connector = GithubConnector(github_owner=github_owner, github_token=github_token)
    members = connector.list_org_members(role=role, include_pending=include_pending)

    # Convert dict to list
    result = []
    for login, data in members.items():
        result.append(
            {
                "login": login,
                "name": data.get("name", ""),
                "email": data.get("email", ""),
                "role": data.get("role", ""),
                "state": data.get("state", ""),
                "avatar_url": data.get("avatar_url", ""),
                "html_url": data.get("html_url", ""),
            }
        )

    return result


def get_repository_file(
    github_owner: str,
    github_token: str,
    github_repo: str,
    file_path: str,
    github_branch: Optional[str] = None,
) -> dict[str, Any]:
    """Get file contents from a repository.

    Args:
        github_owner: GitHub organization name
        github_token: GitHub personal access token
        github_repo: Repository name
        file_path: Path to the file in the repository
        github_branch: Branch name. Defaults to repository's default branch.

    Returns:
        Dict with file content and metadata
    """
    from vendor_connectors.github import GithubConnector

    connector = GithubConnector(
        github_owner=github_owner,
        github_token=github_token,
        github_repo=github_repo,
        github_branch=github_branch,
    )

    # get_repository_file returns (content, sha, path) when both return_sha and return_path are True
    result = connector.get_repository_file(
        file_path=file_path,
        decode=True,
        return_sha=True,
        return_path=True,
    )

    # Unpack the tuple explicitly
    content = result[0] if isinstance(result, tuple) else result
    sha = result[1] if isinstance(result, tuple) and len(result) > 1 else None
    path = result[2] if isinstance(result, tuple) and len(result) > 2 else file_path

    return {
        "path": str(path),
        "content": content,
        "sha": sha,
        "status": "retrieved" if content else "empty",
    }


# =============================================================================
# Tool Definitions
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "github_list_repositories",
        "description": "List repositories in the GitHub organization. Returns repository names, descriptions, and metadata.",
        "func": list_repositories,
    },
    {
        "name": "github_get_repository",
        "description": "Get a specific repository details by name.",
        "func": get_repository,
    },
    {
        "name": "github_list_teams",
        "description": "List teams in the GitHub organization with their metadata.",
        "func": list_teams,
    },
    {
        "name": "github_get_team",
        "description": "Get a specific team details by slug.",
        "func": get_team,
    },
    {
        "name": "github_list_org_members",
        "description": "List members in the GitHub organization with their roles and details.",
        "func": list_org_members,
    },
    {
        "name": "github_get_repository_file",
        "description": "Get file contents from a repository. Returns the file content and metadata.",
        "func": get_repository_file,
    },
]


# =============================================================================
# Framework-Specific Getters
# =============================================================================


def get_langchain_tools() -> list[Any]:
    """Get all GitHub tools as LangChain StructuredTools.

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
    """Get all GitHub tools as CrewAI tools.

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
    """Get all GitHub tools as plain Python functions for AWS Strands.

    Returns:
        List of callable functions.
    """
    return [defn["func"] for defn in TOOL_DEFINITIONS]


def get_tools(framework: str = "auto") -> list[Any]:
    """Get GitHub tools for the specified or auto-detected framework.

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
    "list_repositories",
    "get_repository",
    "list_teams",
    "get_team",
    "list_org_members",
    "get_repository_file",
    # Tool metadata
    "TOOL_DEFINITIONS",
]
