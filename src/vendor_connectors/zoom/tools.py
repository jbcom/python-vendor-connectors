"""AI framework tools for Zoom operations.

This module provides tools for Zoom operations that work with
multiple AI agent frameworks.

Supported Frameworks:
- LangChain (via langchain-core) - get_langchain_tools()
- CrewAI - get_crewai_tools()
- AWS Strands - get_strands_tools() (plain functions)
- Auto-detection - get_tools() picks the best available

Tools provided:
- zoom_list_users: List all Zoom users
- zoom_get_user: Get details of a specific user
- zoom_list_meetings: List meetings for a user
- zoom_get_meeting: Get details of a specific meeting

Usage:
    from vendor_connectors.zoom.tools import get_tools
    tools = get_tools()  # Returns best format for installed framework
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# Input Schemas
# =============================================================================


class ListUsersSchema(BaseModel):
    """Schema for listing Zoom users."""

    max_results: int = Field(100, description="Maximum number of users to return.")


class GetUserSchema(BaseModel):
    """Schema for getting a Zoom user."""

    user_id: str = Field(..., description="User ID or email address.")


class ListMeetingsSchema(BaseModel):
    """Schema for listing Zoom meetings."""

    user_id: str = Field(..., description="User ID or email address.")
    meeting_type: str = Field(
        "scheduled", description="Type of meetings (scheduled, live, upcoming, previous_meetings)."
    )
    max_results: int = Field(100, description="Maximum number of meetings to return.")


class GetMeetingSchema(BaseModel):
    """Schema for getting a Zoom meeting."""

    meeting_id: str = Field(..., description="Meeting ID.")


# =============================================================================
# Tool Implementation Functions
# =============================================================================


def list_users(
    max_results: int = 100,
) -> list[dict[str, Any]]:
    """List all Zoom users.

    Args:
        max_results: Maximum number of users to return

    Returns:
        List of users with their properties (email, id, first_name, last_name, type)
    """
    from vendor_connectors.zoom import ZoomConnector

    connector = ZoomConnector()
    users = connector.list_users()

    # Transform to list format and limit results
    result = []
    for email, user_data in list(users.items())[:max_results]:
        result.append(
            {
                "email": email,
                "id": user_data.get("id", ""),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "type": user_data.get("type", ""),
                "status": user_data.get("status", ""),
            }
        )

    return result


def get_user(
    user_id: str,
) -> dict[str, Any]:
    """Get details of a specific Zoom user.

    Args:
        user_id: User ID or email address

    Returns:
        User data including email, id, first_name, last_name, type, status
    """
    from vendor_connectors.zoom import ZoomConnector

    connector = ZoomConnector()
    user_data = connector.get_user(user_id)

    return {
        "email": user_data.get("email", ""),
        "id": user_data.get("id", ""),
        "first_name": user_data.get("first_name", ""),
        "last_name": user_data.get("last_name", ""),
        "type": user_data.get("type", ""),
        "status": user_data.get("status", ""),
        "timezone": user_data.get("timezone", ""),
        "pmi": user_data.get("pmi", ""),
    }


def list_meetings(
    user_id: str,
    meeting_type: str = "scheduled",
    max_results: int = 100,
) -> list[dict[str, Any]]:
    """List meetings for a specific Zoom user.

    Args:
        user_id: User ID or email address
        meeting_type: Type of meetings (scheduled, live, upcoming, previous_meetings)
        max_results: Maximum number of meetings to return

    Returns:
        List of meetings with their properties (id, topic, start_time, duration, type)
    """
    from vendor_connectors.zoom import ZoomConnector

    connector = ZoomConnector()
    meetings = connector.list_meetings(user_id, meeting_type)

    # Limit results
    result = []
    for meeting in meetings[:max_results]:
        result.append(
            {
                "id": meeting.get("id", ""),
                "uuid": meeting.get("uuid", ""),
                "topic": meeting.get("topic", ""),
                "start_time": meeting.get("start_time", ""),
                "duration": meeting.get("duration", 0),
                "type": meeting.get("type", ""),
                "join_url": meeting.get("join_url", ""),
            }
        )

    return result


def get_meeting(
    meeting_id: str,
) -> dict[str, Any]:
    """Get details of a specific Zoom meeting.

    Args:
        meeting_id: Meeting ID

    Returns:
        Meeting data including id, topic, start_time, duration, join_url, settings
    """
    from vendor_connectors.zoom import ZoomConnector

    connector = ZoomConnector()
    meeting_data = connector.get_meeting(meeting_id)

    return {
        "id": meeting_data.get("id", ""),
        "uuid": meeting_data.get("uuid", ""),
        "topic": meeting_data.get("topic", ""),
        "start_time": meeting_data.get("start_time", ""),
        "duration": meeting_data.get("duration", 0),
        "timezone": meeting_data.get("timezone", ""),
        "type": meeting_data.get("type", ""),
        "join_url": meeting_data.get("join_url", ""),
        "host_id": meeting_data.get("host_id", ""),
        "host_email": meeting_data.get("host_email", ""),
    }


# =============================================================================
# Tool Definitions
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "zoom_list_users",
        "description": "List all Zoom users. Returns user details including email, id, name, and status.",
        "func": list_users,
        "args_schema": ListUsersSchema,
    },
    {
        "name": "zoom_get_user",
        "description": "Get details of a specific Zoom user by ID or email. Returns comprehensive user information.",
        "func": get_user,
        "args_schema": GetUserSchema,
    },
    {
        "name": "zoom_list_meetings",
        "description": "List meetings for a specific user. Returns meeting details including id, topic, start time, and join URL.",
        "func": list_meetings,
        "args_schema": ListMeetingsSchema,
    },
    {
        "name": "zoom_get_meeting",
        "description": "Get details of a specific meeting by meeting ID. Returns comprehensive meeting information.",
        "func": get_meeting,
        "args_schema": GetMeetingSchema,
    },
]


# =============================================================================
# Framework-Specific Getters
# =============================================================================


def get_langchain_tools() -> list[Any]:
    """Get all Zoom tools as LangChain StructuredTools.

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
            args_schema=defn.get("args_schema"),
        )
        for defn in TOOL_DEFINITIONS
    ]


def get_crewai_tools() -> list[Any]:
    """Get all Zoom tools as CrewAI tools.

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
        if "args_schema" in defn:
            wrapped.args_schema = defn["args_schema"]
        tools.append(wrapped)

    return tools


def get_strands_tools() -> list[Any]:
    """Get all Zoom tools as plain Python functions for AWS Strands.

    Returns:
        List of callable functions.
    """
    return [defn["func"] for defn in TOOL_DEFINITIONS]


def get_tools(framework: str = "auto") -> list[Any]:
    """Get Zoom tools for the specified or auto-detected framework.

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
    "list_users",
    "get_user",
    "list_meetings",
    "get_meeting",
    # Tool metadata
    "TOOL_DEFINITIONS",
]
