"""Unified CLI for Vendor Connectors.

This module provides a command-line interface to all vendor connectors.
Use it directly or as a reference for building integrations.

Usage:
    # List available connectors
    vendor-connectors list
    
    # Jules operations
    vendor-connectors jules sources
    vendor-connectors jules create --prompt "Fix the bug" --source sources/github/org/repo
    vendor-connectors jules status sessions/123
    
    # Cursor operations
    vendor-connectors cursor agents
    vendor-connectors cursor launch --prompt "Implement feature X" --repo org/repo
    
    # GitHub operations
    vendor-connectors github repos --owner myorg
    vendor-connectors github issue --owner org --repo name --title "Bug report"
    
    # Start MCP server
    vendor-connectors mcp
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any


def _json_output(data: Any) -> str:
    """Format data as JSON for output."""
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "__iter__") and not isinstance(data, (str, dict)):
        data = [d.model_dump() if hasattr(d, "model_dump") else d for d in data]
    return json.dumps(data, indent=2, default=str)


# =============================================================================
# Jules Commands
# =============================================================================

def cmd_jules_sources(args):
    """List Jules sources."""
    from vendor_connectors.google.jules import JulesConnector
    
    connector = JulesConnector(api_key=args.api_key or os.environ.get("JULES_API_KEY"))
    sources = connector.list_sources()
    print(_json_output(sources))


def cmd_jules_create(args):
    """Create a Jules session."""
    from vendor_connectors.google.jules import JulesConnector
    
    connector = JulesConnector(api_key=args.api_key or os.environ.get("JULES_API_KEY"))
    session = connector.create_session(
        prompt=args.prompt,
        source=args.source,
        title=args.title or "",
        starting_branch=args.branch,
        automation_mode=args.mode,
    )
    print(_json_output(session))


def cmd_jules_status(args):
    """Get Jules session status."""
    from vendor_connectors.google.jules import JulesConnector
    
    connector = JulesConnector(api_key=args.api_key or os.environ.get("JULES_API_KEY"))
    session = connector.get_session(args.session)
    print(_json_output(session))


def cmd_jules_message(args):
    """Send message to Jules session."""
    from vendor_connectors.google.jules import JulesConnector
    
    connector = JulesConnector(api_key=args.api_key or os.environ.get("JULES_API_KEY"))
    session = connector.add_user_response(args.session, args.message)
    print(_json_output(session))


# =============================================================================
# Cursor Commands
# =============================================================================

def cmd_cursor_agents(args):
    """List Cursor agents."""
    from vendor_connectors.cursor import CursorConnector
    
    connector = CursorConnector(api_key=args.api_key or os.environ.get("CURSOR_API_KEY"))
    agents = connector.list_agents()
    print(_json_output(agents))


def cmd_cursor_launch(args):
    """Launch a Cursor agent."""
    from vendor_connectors.cursor import CursorConnector
    
    connector = CursorConnector(api_key=args.api_key or os.environ.get("CURSOR_API_KEY"))
    agent = connector.launch_agent(
        prompt_text=args.prompt,
        repository=args.repo,
        ref=args.ref,
    )
    print(_json_output(agent))


def cmd_cursor_status(args):
    """Get Cursor agent status."""
    from vendor_connectors.cursor import CursorConnector
    
    connector = CursorConnector(api_key=args.api_key or os.environ.get("CURSOR_API_KEY"))
    agent = connector.get_agent(args.agent_id)
    print(_json_output(agent))


# =============================================================================
# GitHub Commands
# =============================================================================

def cmd_github_repos(args):
    """List GitHub repos."""
    from vendor_connectors.github import GitHubConnector
    
    connector = GitHubConnector(token=args.token or os.environ.get("GITHUB_TOKEN"))
    repos = connector.list_repos(owner=args.owner)
    print(_json_output(repos))


def cmd_github_issue(args):
    """Create GitHub issue."""
    from vendor_connectors.github import GitHubConnector
    
    connector = GitHubConnector(token=args.token or os.environ.get("GITHUB_TOKEN"))
    issue = connector.create_issue(
        owner=args.owner,
        repo=args.repo,
        title=args.title,
        body=args.body or "",
    )
    print(_json_output(issue))


# =============================================================================
# MCP Command
# =============================================================================

def cmd_mcp(args):
    """Start MCP server."""
    from vendor_connectors.mcp import main as mcp_main
    return mcp_main()


# =============================================================================
# List Command
# =============================================================================

def cmd_list(args):
    """List available connectors and their status."""
    connectors = {
        "jules": {"env": "JULES_API_KEY", "module": "vendor_connectors.google.jules"},
        "cursor": {"env": "CURSOR_API_KEY", "module": "vendor_connectors.cursor"},
        "github": {"env": "GITHUB_TOKEN", "module": "vendor_connectors.github"},
        "meshy": {"env": "MESHY_API_KEY", "module": "vendor_connectors.meshy"},
        "anthropic": {"env": "ANTHROPIC_API_KEY", "module": "vendor_connectors.anthropic"},
        "aws": {"env": "AWS_ACCESS_KEY_ID", "module": "vendor_connectors.aws"},
        "slack": {"env": "SLACK_TOKEN", "module": "vendor_connectors.slack"},
        "zoom": {"env": "ZOOM_API_KEY", "module": "vendor_connectors.zoom"},
        "vault": {"env": "VAULT_TOKEN", "module": "vendor_connectors.vault"},
    }
    
    print("Available connectors:")
    print("-" * 60)
    for name, info in sorted(connectors.items()):
        env_set = "✓" if os.environ.get(info["env"]) else "✗"
        print(f"  {name:12} [{env_set}] {info['env']}")
    print("-" * 60)
    print("Use: vendor-connectors <connector> --help for more info")


# =============================================================================
# Main CLI
# =============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="vendor-connectors",
        description="Unified CLI for all vendor connectors",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available connectors")
    list_parser.set_defaults(func=cmd_list)
    
    # MCP command
    mcp_parser = subparsers.add_parser("mcp", help="Start MCP server")
    mcp_parser.set_defaults(func=cmd_mcp)
    
    # Jules commands
    jules_parser = subparsers.add_parser("jules", help="Jules AI agent operations")
    jules_parser.add_argument("--api-key", help="Jules API key (or JULES_API_KEY env)")
    jules_sub = jules_parser.add_subparsers(dest="jules_cmd")
    
    jules_sources = jules_sub.add_parser("sources", help="List connected sources")
    jules_sources.set_defaults(func=cmd_jules_sources)
    
    jules_create = jules_sub.add_parser("create", help="Create a session")
    jules_create.add_argument("--prompt", "-p", required=True, help="Task prompt")
    jules_create.add_argument("--source", "-s", required=True, help="Source name")
    jules_create.add_argument("--title", "-t", help="Session title")
    jules_create.add_argument("--branch", "-b", default="main", help="Starting branch")
    jules_create.add_argument("--mode", "-m", default="AUTO_CREATE_PR", help="Automation mode")
    jules_create.set_defaults(func=cmd_jules_create)
    
    jules_status = jules_sub.add_parser("status", help="Get session status")
    jules_status.add_argument("session", help="Session name/ID")
    jules_status.set_defaults(func=cmd_jules_status)
    
    jules_msg = jules_sub.add_parser("message", help="Send message to session")
    jules_msg.add_argument("session", help="Session name/ID")
    jules_msg.add_argument("message", help="Message to send")
    jules_msg.set_defaults(func=cmd_jules_message)
    
    # Cursor commands
    cursor_parser = subparsers.add_parser("cursor", help="Cursor cloud agent operations")
    cursor_parser.add_argument("--api-key", help="Cursor API key (or CURSOR_API_KEY env)")
    cursor_sub = cursor_parser.add_subparsers(dest="cursor_cmd")
    
    cursor_agents = cursor_sub.add_parser("agents", help="List agents")
    cursor_agents.set_defaults(func=cmd_cursor_agents)
    
    cursor_launch = cursor_sub.add_parser("launch", help="Launch an agent")
    cursor_launch.add_argument("--prompt", "-p", required=True, help="Task prompt")
    cursor_launch.add_argument("--repo", "-r", help="GitHub repo (org/name)")
    cursor_launch.add_argument("--ref", default="main", help="Git ref")
    cursor_launch.set_defaults(func=cmd_cursor_launch)
    
    cursor_status = cursor_sub.add_parser("status", help="Get agent status")
    cursor_status.add_argument("agent_id", help="Agent ID")
    cursor_status.set_defaults(func=cmd_cursor_status)
    
    # GitHub commands
    github_parser = subparsers.add_parser("github", help="GitHub operations")
    github_parser.add_argument("--token", help="GitHub token (or GITHUB_TOKEN env)")
    github_sub = github_parser.add_subparsers(dest="github_cmd")
    
    github_repos = github_sub.add_parser("repos", help="List repos")
    github_repos.add_argument("--owner", "-o", help="User or org name")
    github_repos.set_defaults(func=cmd_github_repos)
    
    github_issue = github_sub.add_parser("issue", help="Create issue")
    github_issue.add_argument("--owner", "-o", required=True, help="Repo owner")
    github_issue.add_argument("--repo", "-r", required=True, help="Repo name")
    github_issue.add_argument("--title", "-t", required=True, help="Issue title")
    github_issue.add_argument("--body", "-b", help="Issue body")
    github_issue.set_defaults(func=cmd_github_issue)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if hasattr(args, "func"):
        try:
            result = args.func(args)
            return result if result is not None else 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
