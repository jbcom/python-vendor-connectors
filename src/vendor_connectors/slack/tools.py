"""AI framework tools for Slack operations.

This module provides tools for Slack operations that work with multiple
AI agent frameworks.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

# =============================================================================
# Input Schemas
# =============================================================================


class SendMessageSchema(BaseModel):
    """Schema for sending a Slack message."""

    channel: str = Field(..., description="The name of the channel to send the message to (without #).")
    text: str = Field(..., description="The text content of the message.")
    thread_ts: Optional[str] = Field(None, description="Optional thread timestamp to reply in a thread.")


class ListUsersSchema(BaseModel):
    """Schema for listing Slack users."""

    include_bots: bool = Field(False, description="Whether to include bot accounts.")
    limit: int = Field(100, description="Maximum number of users to return.")


class ListConversationsSchema(BaseModel):
    """Schema for listing Slack conversations."""

    types: str = Field(
        "public_channel,private_channel",
        description="Comma-separated list of conversation types (public_channel, private_channel, im, mpim).",
    )
    limit: int = Field(100, description="Maximum number of conversations to return.")


# =============================================================================
# Tool Implementation Functions
# =============================================================================


def slack_send_message(
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
) -> str:
    """Send a message to a Slack channel.

    Args:
        channel: Channel name (without #).
        text: Message text.
        thread_ts: Optional thread timestamp.

    Returns:
        Timestamp of the posted message.
    """
    from vendor_connectors.slack import SlackConnector

    connector = SlackConnector()
    return connector.send_message(channel_name=channel, text=text, thread_id=thread_ts)


def slack_list_users(
    include_bots: bool = False,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """List Slack users.

    Args:
        include_bots: Include bot accounts.
        limit: Max users to return.

    Returns:
        List of user profiles.
    """
    from vendor_connectors.slack import SlackConnector

    connector = SlackConnector()
    users = connector.list_users(include_bots=include_bots, limit=limit)
    return list(users.values())


def slack_list_channels(
    types: str = "public_channel,private_channel",
    limit: int = 100,
) -> list[dict[str, Any]]:
    """List Slack channels/conversations.

    Args:
        types: Conversation types.
        limit: Max results.

    Returns:
        List of conversation metadata.
    """
    from vendor_connectors.slack import SlackConnector

    connector = SlackConnector()
    channels = connector.list_conversations(types=types, limit=limit)
    return list(channels.values())


# =============================================================================
# Tool Definitions
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "slack_send_message",
        "description": "Send a message to a Slack channel. Useful for notifications or replies.",
        "func": slack_send_message,
        "args_schema": SendMessageSchema,
    },
    {
        "name": "slack_list_users",
        "description": "List users in the Slack workspace. Useful for finding member IDs or emails.",
        "func": slack_list_users,
        "args_schema": ListUsersSchema,
    },
    {
        "name": "slack_list_channels",
        "description": "List available Slack channels and conversations.",
        "func": slack_list_channels,
        "args_schema": ListConversationsSchema,
    },
]


# =============================================================================
# Framework-Specific Getters
# =============================================================================


def get_langchain_tools() -> list[Any]:
    """Get all Slack tools as LangChain StructuredTools."""
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
    """Get all Slack tools as CrewAI tools."""
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
    """Get all Slack tools as plain Python functions."""
    return [defn["func"] for defn in TOOL_DEFINITIONS]


def get_tools(framework: str = "auto") -> list[Any]:
    """Get Slack tools for the specified or auto-detected framework."""
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
    "slack_send_message",
    "slack_list_users",
    "slack_list_channels",
    "TOOL_DEFINITIONS",
]
