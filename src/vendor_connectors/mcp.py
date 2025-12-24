"""Unified MCP Server for Vendor Connectors.

This module provides a single MCP (Model Context Protocol) server that
exposes ALL vendor connectors as tools. Connect once, access everything.

Usage:
    # Command line
    python -m vendor_connectors.mcp
    
    # Or via entry point
    vendor-connectors-mcp

Configure in Claude Desktop or any MCP client:
    {
      "mcpServers": {
        "vendor-connectors": {
          "command": "vendor-connectors-mcp",
          "env": {
            "CURSOR_API_KEY": "...",
            "JULES_API_KEY": "...",
            "GITHUB_TOKEN": "...",
            "MESHY_API_KEY": "..."
          }
        }
      }
    }

This provides the bridge between TypeScript (@agentic/control) and Python
(vendor-connectors) with zero custom code - just standard MCP over stdio.
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional

# Lazy imports for optional dependencies
def _check_mcp():
    try:
        import mcp
        return True
    except ImportError:
        return False


def create_server():
    """Create the unified MCP server with all available connectors."""
    try:
        from mcp.server import Server
        from mcp.types import Tool, TextContent
    except ImportError as e:
        raise ImportError(
            "MCP SDK not installed. Install with: pip install vendor-connectors[mcp]"
        ) from e

    server = Server("vendor-connectors")
    
    # =========================================================================
    # Tool Registry - All connectors expose their tools here
    # =========================================================================
    
    TOOLS: dict[str, dict] = {}
    
    # -------------------------------------------------------------------------
    # Jules Tools (Google)
    # -------------------------------------------------------------------------
    
    def _get_jules():
        from vendor_connectors.google.jules import JulesConnector
        api_key = os.environ.get("JULES_API_KEY")
        if not api_key:
            raise ValueError("JULES_API_KEY environment variable required")
        return JulesConnector(api_key=api_key)
    
    TOOLS["jules_list_sources"] = {
        "description": "List available GitHub repositories connected to Jules",
        "parameters": {
            "type": "object",
            "properties": {
                "page_size": {"type": "integer", "default": 100, "description": "Max results"}
            }
        },
        "handler": lambda params: _get_jules().list_sources(params.get("page_size", 100))
    }
    
    TOOLS["jules_create_session"] = {
        "description": "Create a Jules session to work on a coding task. Returns session info with ID to poll.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Task description for Jules"},
                "source": {"type": "string", "description": "Source name (e.g., sources/github/org/repo)"},
                "title": {"type": "string", "description": "Optional session title"},
                "starting_branch": {"type": "string", "default": "main", "description": "Git branch"},
                "automation_mode": {"type": "string", "default": "AUTO_CREATE_PR", "description": "AUTO_CREATE_PR or MANUAL"}
            },
            "required": ["prompt", "source"]
        },
        "handler": lambda params: _get_jules().create_session(
            prompt=params["prompt"],
            source=params["source"],
            title=params.get("title", ""),
            starting_branch=params.get("starting_branch", "main"),
            automation_mode=params.get("automation_mode", "AUTO_CREATE_PR")
        )
    }
    
    TOOLS["jules_get_session"] = {
        "description": "Get the current status of a Jules session",
        "parameters": {
            "type": "object",
            "properties": {
                "session_name": {"type": "string", "description": "Session name (e.g., sessions/123)"}
            },
            "required": ["session_name"]
        },
        "handler": lambda params: _get_jules().get_session(params["session_name"])
    }
    
    TOOLS["jules_add_message"] = {
        "description": "Send a follow-up message to a Jules session",
        "parameters": {
            "type": "object",
            "properties": {
                "session_name": {"type": "string", "description": "Session name"},
                "message": {"type": "string", "description": "Message to send"}
            },
            "required": ["session_name", "message"]
        },
        "handler": lambda params: _get_jules().add_user_response(params["session_name"], params["message"])
    }
    
    # -------------------------------------------------------------------------
    # Cursor Tools
    # -------------------------------------------------------------------------
    
    def _get_cursor():
        from vendor_connectors.cursor import CursorConnector
        api_key = os.environ.get("CURSOR_API_KEY")
        if not api_key:
            raise ValueError("CURSOR_API_KEY environment variable required")
        return CursorConnector(api_key=api_key)
    
    TOOLS["cursor_list_agents"] = {
        "description": "List Cursor cloud agents",
        "parameters": {"type": "object", "properties": {}},
        "handler": lambda params: _get_cursor().list_agents()
    }
    
    TOOLS["cursor_launch_agent"] = {
        "description": "Launch a Cursor cloud agent for a coding task (expensive!)",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Task description"},
                "repository": {"type": "string", "description": "GitHub repo (org/name)"},
                "ref": {"type": "string", "default": "main", "description": "Git ref"}
            },
            "required": ["prompt"]
        },
        "handler": lambda params: _get_cursor().launch_agent(
            prompt_text=params["prompt"],
            repository=params.get("repository"),
            ref=params.get("ref", "main")
        )
    }
    
    TOOLS["cursor_get_agent"] = {
        "description": "Get status of a Cursor agent",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent ID"}
            },
            "required": ["agent_id"]
        },
        "handler": lambda params: _get_cursor().get_agent(params["agent_id"])
    }
    
    # -------------------------------------------------------------------------
    # GitHub Tools
    # -------------------------------------------------------------------------
    
    def _get_github():
        from vendor_connectors.github import GitHubConnector
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable required")
        return GitHubConnector(token=token)
    
    TOOLS["github_list_repos"] = {
        "description": "List GitHub repositories for a user or organization",
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "User or org name"},
                "type": {"type": "string", "default": "all", "description": "all, owner, member"}
            }
        },
        "handler": lambda params: _get_github().list_repos(
            owner=params.get("owner"),
            repo_type=params.get("type", "all")
        )
    }
    
    TOOLS["github_create_issue"] = {
        "description": "Create a GitHub issue",
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repo owner"},
                "repo": {"type": "string", "description": "Repo name"},
                "title": {"type": "string", "description": "Issue title"},
                "body": {"type": "string", "description": "Issue body"}
            },
            "required": ["owner", "repo", "title"]
        },
        "handler": lambda params: _get_github().create_issue(
            owner=params["owner"],
            repo=params["repo"],
            title=params["title"],
            body=params.get("body", "")
        )
    }
    
    # -------------------------------------------------------------------------
    # Meshy Tools (3D Generation)
    # -------------------------------------------------------------------------
    
    def _get_meshy():
        from vendor_connectors.meshy import MeshyConnector
        api_key = os.environ.get("MESHY_API_KEY")
        if not api_key:
            raise ValueError("MESHY_API_KEY environment variable required")
        return MeshyConnector(api_key=api_key)
    
    TOOLS["meshy_text_to_3d"] = {
        "description": "Generate a 3D model from text description",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Text description of the 3D model"},
                "art_style": {"type": "string", "default": "realistic", "description": "realistic or sculpture"},
                "target_polycount": {"type": "integer", "default": 30000}
            },
            "required": ["prompt"]
        },
        "handler": lambda params: _get_meshy().text_to_3d(
            prompt=params["prompt"],
            art_style=params.get("art_style", "realistic"),
            target_polycount=params.get("target_polycount", 30000)
        )
    }
    
    # =========================================================================
    # MCP Server Handlers
    # =========================================================================
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """Return all available tools."""
        return [
            Tool(
                name=name,
                description=tool["description"],
                inputSchema=tool["parameters"]
            )
            for name, tool in TOOLS.items()
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Execute a tool and return results."""
        if name not in TOOLS:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        try:
            result = TOOLS[name]["handler"](arguments)
            # Convert Pydantic models to dict
            if hasattr(result, "model_dump"):
                result = result.model_dump()
            elif hasattr(result, "__iter__") and not isinstance(result, (str, dict)):
                result = [r.model_dump() if hasattr(r, "model_dump") else r for r in result]
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]
    
    return server


def main():
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
